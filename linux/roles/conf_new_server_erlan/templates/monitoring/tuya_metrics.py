#!/usr/bin/env python3

import hashlib
import hmac
import json
import os
import subprocess
import sys
import time
from urllib.parse import urlparse

import requests

TUYA_ACCESS_ID = os.environ["TUYA_ACCESS_ID"]
TUYA_ACCESS_SECRET = os.environ["TUYA_ACCESS_SECRET"]
TUYA_REGION = os.getenv("TUYA_REGION", "eu")

TUYA_DEVICE_ID = sys.argv[1]

ZABBIX_SERVER = os.getenv("ZABBIX_SERVER")
ZABBIX_PORT = os.getenv("ZABBIX_PORT", "10051")
ZABBIX_HOST = os.getenv("ZABBIX_HOST", TUYA_DEVICE_ID)

# Региональные endpoint'ы Tuya могут отличаться.
TUYA_BASE_URLS = {
    "eu": "https://openapi.tuyaeu.com",
    "us": "https://openapi.tuyaus.com",
    "cn": "https://openapi.tuyacn.com",
    "in": "https://openapi.tuyain.com",
}


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_tuya_headers(method: str, path: str, body: str = "") -> dict:
    """
    Формирование подписи Tuya Cloud API для запроса без access_token.
    Для запросов с токеном подпись дополняется access_token.
    """
    timestamp = str(int(time.time() * 1000))
    body_hash = sha256_hex(body)

    # Строка, которую подписывает Tuya.
    string_to_sign = "\n".join([
        method.upper(),
        body_hash,
        "",
        path,
    ])

    sign_message = (
        TUYA_ACCESS_ID
        + timestamp
        + string_to_sign
    )

    signature = hmac.new(
        TUYA_ACCESS_SECRET.encode("utf-8"),
        sign_message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest().upper()

    return {
        "client_id": TUYA_ACCESS_ID,
        "t": timestamp,
        "sign": signature,
        "sign_method": "HMAC-SHA256",
        "Content-Type": "application/json",
    }


def get_access_token(base_url: str) -> str:
    path = "/v1.0/token?grant_type=1"
    url = base_url + path
    body = ""

    headers = build_tuya_headers("GET", path, body)

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    result = response.json()

    if not result.get("success"):
        raise RuntimeError(f"Tuya token error: {result}")

    return result["result"]["access_token"]


def get_device_status(base_url: str, access_token: str, device_id: str) -> list:
    path = f"/v1.0/devices/{device_id}/status"
    url = base_url + path
    body = ""

    timestamp = str(int(time.time() * 1000))
    body_hash = sha256_hex(body)

    string_to_sign = "\n".join([
        "GET",
        body_hash,
        "",
        path,
    ])

    sign_message = (
        TUYA_ACCESS_ID
        + access_token
        + timestamp
        + string_to_sign
    )

    signature = hmac.new(
        TUYA_ACCESS_SECRET.encode("utf-8"),
        sign_message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest().upper()

    headers = {
        "client_id": TUYA_ACCESS_ID,
        "access_token": access_token,
        "t": timestamp,
        "sign": signature,
        "sign_method": "HMAC-SHA256",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    result = response.json()

    if not result.get("success"):
        raise RuntimeError(f"Tuya status error: {result}")

    return result["result"]


def normalize_value(value):
    """
    Преобразование Tuya-значения в формат для Zabbix.
    Tuya может возвращать числа, строки, boolean и другие типы.
    """
    if isinstance(value, bool):
        return int(value)

    if isinstance(value, (int, float)):
        return value

    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return value

    return str(value)


def send_to_zabbix(values: dict):
    """
    Передача метрик через zabbix_sender.
    """
    payload = []

    for key, value in values.items():
        payload.append(f"{ZABBIX_HOST} {key} {value}")
        # print(f"{key} {value}")

    process = subprocess.run(
        [
            "zabbix_sender",
            "-z", ZABBIX_SERVER,
            "-p", ZABBIX_PORT,
            "-i", "-"
        ],
        input="\n".join(payload) + "\n",
        text=True,
        capture_output=True,
        check=False,
    )

    if process.returncode != 0:
        raise RuntimeError(
            "zabbix_sender завершился с ошибкой:\n"
            + process.stdout
            + process.stderr
        )

    print(process.stdout)


def main():
    base_url = TUYA_BASE_URLS[TUYA_REGION]

    access_token = get_access_token(base_url)
    statuses = get_device_status(base_url, access_token, TUYA_DEVICE_ID)

    # Полезно на первом запуске посмотреть полный список datapoint'ов.
    # print(json.dumps(statuses, ensure_ascii=False, indent=2))

    values = {}

    for item in statuses:
        code = item.get("code")
        value = item.get("value")

        if not code:
            continue

        # В Zabbix ключ будет выглядеть, например:
        # tuya.raw[abcdef123456,va_temperature]
        zabbix_key = f"tuya.raw[{code}]"

        normalized = normalize_value(value)

        # Передаём только числовые значения.
        if isinstance(normalized, (int, float)):
            values[zabbix_key] = normalized

    if values:
        send_to_zabbix(values)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(1)
