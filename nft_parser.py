def parse_nft_collection(res):
    try:
        arr = res["data"]["array"]
    except:
        return []

    miners = []
    for w in arr:
        if "data" in w and w["data"]:
            for m in w["data"]:
                miners.append({
                    "name": m.get("nftName", "Unknown"),
                    "power": m.get("nftPower", "?")
                })

    return miners
