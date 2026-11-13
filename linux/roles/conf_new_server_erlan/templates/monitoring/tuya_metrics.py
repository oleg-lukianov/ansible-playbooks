#!/usr/bin/env python3

import hashlib
import hmac
import json
import os
import subprocess
import sys
import time
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime

import requests

if len(sys.argv) < 2:
    print(f"Example run: {sys.argv[0]} \"TUYA_DEVICE_ID\" \"-send-metrics\"")
    print(f"Example run: {sys.argv[0]} \"TUYA_DEVICE_ID\" \"-discovery\"")
    print(f"Example run: {sys.argv[0]} \"TUYA_DEVICE_ID\" \"-raw\"")
    sys.exit()

config_path = Path(__file__).resolve().parent / "tuya.conf"
config = {}

with config_path.open(encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        line = line.strip()

        # Пропускаємо порожні рядки та коментарі
        if not line or line.startswith("#"):
            continue

        key, separator, value = line.partition("=")

        if not separator or not key.strip():
            raise ValueError(f"Некоректний рядок {line_number} у test.conf")

        config[key.strip()] = value.strip()

TUYA_ACCESS_ID = config["TUYA_ACCESS_ID"]
TUYA_ACCESS_SECRET = config["TUYA_ACCESS_SECRET"]
ZABBIX_SERVER = config["ZABBIX_SERVER"]
TUYA_REGION = os.getenv("TUYA_REGION", "eu")
TUYA_DEVICE_ID = sys.argv[1]

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
    today = datetime.now()
    format_date = today.strftime("%d.%m.%Y %H:%M:%S")
    print(f"{format_date} - TUYA_DEVICE_ID={TUYA_DEVICE_ID} - ", end='', flush=True)
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

    print(process.stdout, end='', flush=True)


def device_metrics_to_text(statuses):
    """
    Преобразует ответ Tuya со статусами устройства в читаемый текст.

    statuses должен иметь формат:
    [
        {
            "code": "switch_1",
            "value": true,
            " t": 123456789
        },
        ...
    ]

    Возвращает строку.
    """

    if not statuses:
        return "Tuya не вернула метрики устройства"

    lines = []

    for item in statuses:
        code = item.get("code", "unknown")
        value = item.get("value")

        # Дополнительные поля Tuya, если они присутствуют
        extra = []

        if "value" not in item:
            value = "<нет значения>"

        if "unit" in item:
            extra.append(f"единица={item['unit']}")

        if "t" in item:
            extra.append(f"время={item['t']}")

        suffix = f" ({', '.join(extra)})" if extra else ""

        lines.append(f"{code}: {value}{suffix}")

    return "\n".join(lines)


def print_device_metrics(base_url, access_token, device_id):
    statuses = get_device_status(
        base_url=base_url,
        access_token=access_token,
        device_id=device_id,
    )

    text = device_metrics_to_text(statuses)
    print(text)

    return text


def device_metrics_to_json(statuses):
    """
    Возвращает все datapoint'ы устройства в виде JSON-текста.
    """

    return json.dumps(
        statuses,
        ensure_ascii=False,
        indent=2,
    )


def main():
    base_url = TUYA_BASE_URLS[TUYA_REGION]

    access_token = get_access_token(base_url)
    statuses = get_device_status(base_url, access_token, TUYA_DEVICE_ID)

    # Полезно на первом запуске посмотреть полный список datapoint'ов.
    if ("-discovery" == sys.argv[2]):
        print(json.dumps(statuses, ensure_ascii=False, sort_keys=True, indent=2))
    if ("-raw" == sys.argv[2]):
        print(device_metrics_to_json(statuses))
    else:
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
