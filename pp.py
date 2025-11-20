def get_token_price(symbol: str):
    return call_api("GET", f"/api/exchanges/getPrice?symbol={symbol}")
