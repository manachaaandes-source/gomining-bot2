from telegram.ext import ApplicationBuilder, CommandHandler
from gomining_api import get_balance, get_nft, get_market_stats
from nft_parser import parse_nft_collection
from config import TELEGRAM_BOT_TOKEN
import requests

# --- Coingecko 価格取得 ---
def get_price(symbol):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        res = requests.get(url, timeout=5).json()
        return float(res[symbol]["usd"])
    except:
        return 0.0


# ============================
# /start
# ============================
async def start(update, ctx):
    msg = (
        "🔥 GoMining Bot 起動！\n\n"
        "/balance → ウォレット残高（USD換算付き）\n"
        "/nft → Miner一覧\n"
        "/power → 総 TH/s\n"
        "/income → 今日 + 全期間収益\n"
        "/stats → GMT 市場データ\n"
    )
    await update.message.reply_text(msg)


# ============================
# /balance
# ============================
async def balance(update, ctx):
    res = get_balance()

    if "data" not in res or "array" not in res["data"]:
        return await update.message.reply_text("❌ balance error\n" + str(res))

    wallets = res["data"]["array"]

    price_cache = {
        "BTC": get_price("bitcoin"),
        "GMT": get_price("gmt-token"),
        "ETH": get_price("ethereum"),
        "SOL": get_price("solana"),
        "BNB": get_price("binancecoin"),
        "TON": get_price("the-open-network"),
        "USDT": 1.0,
        "USDC": 1.0,
    }

    msg = "💰 Wallet Balances:\n\n"

    for w in wallets:
        token = w["type"].replace("VIRTUAL_", "")
        raw = int(w.get("valueNumericAtSyncDate", "0"))

        # --- 正しい変換 ---
        if token == "GMT":
            value = float(w.get("gmtValueAtSyncDate", 0))
        else:
            value = raw / 1e18

        usd = value * price_cache.get(token, 0)

        # BTCだけは桁合わせ
        if token == "BTC":
            v = f"{value:.8f}"
        else:
            v = f"{value}"

        msg += f"• {token}: {v}   (${usd:.6f})\n"

    await update.message.reply_text(msg)


# ============================
# /nft
# ============================
async def nft(update, ctx):
    res = get_nft()
    miners = parse_nft_collection(res)

    if not miners:
        return await update.message.reply_text("❌ NFT 取得失敗")

    msg = "⛏ Miner List:\n"
    for m in miners[:50]:
        msg += f"\n• {m['name']} — {m['power']} TH/s"

    await update.message.reply_text(msg)


# ============================
# /power
# ============================
async def power(update, ctx):
    data = get_nft()

    if "data" not in data or "array" not in data["data"]:
        return await update.message.reply_text("❌ NFTデータ取得失敗")

    total_power = 0.0
    for nft in data["data"]["array"]:
        total_power += float(nft.get("eligiblePower", 0))

    msg = f"⚡ Total Mining Power\n{total_power:.4f} TH/s"
    await update.message.reply_text(msg)


# ============================
# /income
# ============================
async def income(update, ctx):
    data = get_nft()

    if "data" not in data or "array" not in data["data"]:
        return await update.message.reply_text("❌ NFTデータ取得失敗")

    total_today_btc = 0
    total_all_btc = 0

    for nft in data["data"]["array"]:
        power = float(nft.get("eligiblePower", 0))
        agg = nft.get("nftIncomeAggregation")
        if not agg:
            continue

        btc_usd = float(agg.get("btcCourseInUsd", 0))

        # 今日
        c_today = float(agg.get("totalIncomePerThToday", 0))
        total_today_btc += power * c_today / btc_usd

        # 全期間
        c_total = float(agg.get("totalIncomePerTh", 0))
        total_all_btc += power * c_total / btc_usd

    msg = (
        "💸 Mining Income\n\n"
        f"📅 Today: {total_today_btc:.10f} BTC\n"
        f"📦 Total: {total_all_btc:.10f} BTC\n"
    )

    await update.message.reply_text(msg)


# ============================
# /stats
# ============================
async def stats(update, ctx):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=gmt-token&vs_currencies=usd"
        price = requests.get(url).json()["gmt-token"]["usd"]
        await update.message.reply_text(f"📊 GMT Market Price\n${price}")
    except:
        await update.message.reply_text("❌ stats error (Coingecko)")


# ============================
# BOT main
# ============================
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("nft", nft))
    app.add_handler(CommandHandler("power", power))
    app.add_handler(CommandHandler("income", income))
    app.add_handler(CommandHandler("stats", stats))

    print("🚀 Bot started! Listening...")
    app.run_polling()


if __name__ == "__main__":
    main()
