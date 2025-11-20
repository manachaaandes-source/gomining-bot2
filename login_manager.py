import requests
from token_manager import load_tokens, save_tokens
from config import API_BASE, GM_EMAIL, GM_PASSWORD, TURNSTILE_TOKEN


# -----------------------------
# 初回ログイン（通常は1回だけでOK）
# -----------------------------
def login():
    url = API_BASE + "/api/auth/login"

    payload = {
        "email": GM_EMAIL,
        "password": GM_PASSWORD,
        "turnstileToken": TURNSTILE_TOKEN
    }

    r = requests.post(url, json=payload)
    data = r.json()

    if "data" not in data:
        raise Exception("Login failed: " + str(data))

    jwt = data["data"]["accessToken"]
    refresh = data["data"]["refreshToken"]

    save_tokens(jwt, refresh)
    return jwt


# -----------------------------
# refreshToken → 新しい accessToken 取得
# -----------------------------
def refresh_by_token(refresh_token):
    url = API_BASE + "/api/auth/refresh"

    payload = {"refreshToken": refresh_token}

    r = requests.post(url, json=payload)
    data = r.json()

    if "data" not in data:
        raise Exception("Refresh failed: " + str(data))

    new_access = data["data"]["accessToken"]
    new_refresh = data["data"]["refreshToken"]

    save_tokens(new_access, new_refresh)
    return new_access


# -----------------------------
# 永久に accessToken を維持する関数
# -----------------------------
def ensure_login():
    tokens = load_tokens()
    access = tokens.get("access")
    refresh = tokens.get("refresh")

    # 1. accessToken があるならそのまま使う
    if access:
        return access

    # 2. access 不在なら refresh
    if refresh:
        try:
            return refresh_by_token(refresh)
        except Exception as e:
            print("Refresh failed:", e)

    # 3. refresh もダメ → 初回ログインし直す
    return login()
