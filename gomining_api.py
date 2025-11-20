import requests
from config import API_BASE
from login_manager import ensure_login


def call_api(method, path, body=None):
    access = ensure_login()

    headers = {
        "Authorization": f"Bearer {access}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    url = API_BASE + path

    try:
        if method == "GET":
            r = requests.get(url, headers=headers)
        else:
            r = requests.post(url, headers=headers, json=body)

        return r.json()
    except Exception as e:
        return {"error": str(e)}


# ---------------------------
# ウォレット残高
# ---------------------------
def get_balance():
    return call_api(
        "POST",
        "/api/wallet/find-by-user",
        body={"pagination": {"skip": 0, "limit": 50}}
    )


# ---------------------------
# NFT（Miner 持ち物一覧）
# ---------------------------
def get_nft():
    return call_api("POST", "/api/nft/get-my", body={})



# ---------------------------
# GMT 関連の市場データ
# ただしこれは GMT の総支払い額で「価格」ではない
# ---------------------------
def get_market_stats():
    return call_api("GET", "/api/payment-marketplace-statistics")
