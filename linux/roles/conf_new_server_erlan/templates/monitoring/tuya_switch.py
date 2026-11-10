#!/usr/bin/env python3

import hashlib
import hmac
import json
import os
import sys
import time

import requests

TUYA_ACCESS_ID = os.environ["TUYA_ACCESS_ID"]
TUYA_ACCESS_SECRET = os.environ["TUYA_ACCESS_SECRET"]
TUYA_DEVICE_ID = os.environ["TUYA_DEVICE_ID"]
TUYA_REGION = os.getenv("TUYA_REGION", "eu")

# Обычно для европейского региона:
TUYA_BASE_URLS = {
    "eu": "https://openapi.tuyaeu.com",
    "us": "https://openapi.tuyaus.com",
    "cn": "https://openapi.tuyacn.com",
    "in": "https://openapi.tuyain.com",
}

BASE_URL = TUYA_BASE_URLS[TUYA_REGION]

# Для большинства умных розеток:
SWITCH_CODE = os.getenv("TUYA_SWITCH_CODE", "switch_1")


def sha256_hex(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def make_signature(
    method: str,
    path: str,
    body: str,
    access_token: str = "",
):
    """
    Формирование подписи Tuya Cloud API.
    """

    timestamp = str(int(time.time() * 1000))
    body_hash = sha256_hex(body)

    # Для POST-запроса тело должно входить в строку подписи.
    string_to_sign = "\n".join([
        method.upper(),
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

    sign = hmac.new(
        TUYA_ACCESS_SECRET.encode("utf-8"),
        sign_message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest().upper()

    headers = {
        "client_id": TUYA_ACCESS_ID,
        "access_token": access_token,
        "t": timestamp,
        "sign": sign,
        "sign_method": "HMAC-SHA256",
        "Content-Type": "application/json",
    }

    return headers


def get_access_token() -> str:
    path = "/v1.0/token?grant_type=1"
    url = BASE_URL + path

    headers = make_signature(
        method="GET",
        path=path,
        body="",
        access_token="",
    )

    response = requests.get(
        url,
        headers=headers,
        timeout=15,
    )

    response.raise_for_status()
    result = response.json()

    if not result.get("success"):
        raise RuntimeError(f"Ошибка получения токена: {result}")

    return result["result"]["access_token"]


def send_switch_command(access_token: str, enabled: bool):
    path = f"/v1.0/devices/{TUYA_DEVICE_ID}/commands"
    url = BASE_URL + path

    # Важно: separators позволяют получить компактный JSON.
    # Именно эта строка body должна использоваться и в запросе,
    # и при расчёте подписи.
    body_dict = {
        "commands": [
            {
                "code": SWITCH_CODE,
                "value": enabled,
            }
        ]
    }

    body = json.dumps(
        body_dict,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    headers = make_signature(
        method="POST",
        path=path,
        body=body,
        access_token=access_token,
    )

    response = requests.post(
        url,
        headers=headers,
        data=body.encode("utf-8"),
        timeout=15,
    )

    response.raise_for_status()
    result = response.json()

    if not result.get("success"):
        raise RuntimeError(f"Ошибка управления розеткой: {result}")

    state = "включена" if enabled else "выключена"
    print(f"Розетка успешно {state}")
    print(result)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("on", "off"):
        print(f"Использование: {sys.argv[0]} on|off")
        print(f"Пример: {sys.argv[0]} on")
        sys.exit(2)

    command = sys.argv[1]
    enabled = command == "on"

    access_token = get_access_token()
    send_switch_command(access_token, enabled)


if __name__ == "__main__":
    try:
        main()
    except KeyError as error:
        print(
            f"Не задана переменная окружения: {error.args[0]}",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(1)
