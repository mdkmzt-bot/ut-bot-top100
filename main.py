import os
import requests
import pandas as pd
import time

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

TOP_100 = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT","DOGEUSDT","TRXUSDT","AVAXUSDT","SHIBUSDT",
           "LINKUSDT","DOTUSDT","TONUSDT","MATICUSDT","LTCUSDT","BCHUSDT","NEARUSDT","HBARUSDT","ICPUSDT","APTUSDT",
           "VETUSDT","ATOMUSDT","LEOUSDT","FILUSDT","ETCUSDT","STXUSDT","XLMUSDT","XMRUSDT","IMXUSDT","AAVEUSDT",
           "INJUSDT","OPUSDT","CROUSDT","ARUSDT","SUIUSDT","FDUSDUSDT","RNDRUSDT","MKRUSDT","ALGOUSDT","GRTUSDT",
           "THETAUSDT","FLOWUSDT","FTMUSDT","BGBUSDT","RUNEUSDT","HNTUSDT","QNTUSDT","GALAUSDT","SEIUSDT","BEAMUSDT",
           "FLRUSDT","EOSUSDT","XTZUSDT","AXSUSDT","NEOUSDT","KCSUSDT","SANDUSDT","DYDXUSDT","BTTUSDT","MANAUSDT",
           "USDDUSDT","CHZUSDT","KAIAUSDT","PENDLEUSDT","APEUSDT","CAKEUSDT","IOTAUSDT","WLDUSDT","LUNCUSDT","ROSEUSDT",
           "XECUSDT","CFXUSDT","AKTUSDT","TKXUSDT","PYTHUSDT","ZECUSDT","TUSDT","FTTUSDT","GTUSDT","NEXOUSDT",
           "SNXUSDT","XAUtUSDT","COMPUSDT","WOOUSDT","KAVAUSDT","TFUELUSDT","CRVUSDT","1INCHUSDT","IOTXUSDT","ASTRUSDT",
           "GLMUSDT","KSMUSDT","CELOUSDT","ENJUSDT","DYMUSDT","SUPERUSDT","ANKRUSDT","LUNAUSDT","JSTUSDT","ETHWUSDT"]

def tg(msg):
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                     params={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def get_price_change(s): 
    try: 
        d = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={s}", timeout=8).json()
        return float(d["priceChangePercent"]), float(d["lastPrice"])
    except: return 0,0

def get_data(s):
    try:
        df = pd.DataFrame(requests.get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval=5m&limit=200", timeout=8).json())
        df = df.iloc[:,[1,2,3,4]].astype(float); df.columns=["open","high","low","close"]
        return df
    except: return None

def ut_bot_alerts(df):
    key=2; atr=df["high"].rolling(1).max()-df["low"].rolling(1).min(); nLoss=key*atr
    ts=[df["close"].iloc[0]]
    for i in range(1,len(df)):
        ts.append(max(ts[-1], df["close"].iloc[i]-nLoss.iloc[i]) if df["close"].iloc[i]>ts[-1] else df["close"].iloc[i]+nLoss.iloc[i])
    df["ts"]=ts
    buy=(df["close"]>df["ts"]) & (df["close"].shift(1)<=df["ts"].shift(1))
    sell=(df["close"]<df["ts"]) & (df["close"].shift(1)>=df["ts"].shift(1))
    return buy.iloc[-1], sell.iloc[-1]

last_signal = {}
print("UT Bot Top-100 LIVE 24/7! 🚀")
tg("Bot started – monitoring Top 100 coins!")

while True:
    for p in TOP_100:
        df = get_data(p)
        if not df or len(df) < 50: continue
        buy, sell = ut_bot_alerts(df)
        sig = "BUY" if buy else "SELL" if sell else None
        if sig and last_signal.get(p) != sig:
            ch, pr = get_price_change(p)
            arrow = "Long" if sig == "BUY" else "Short"
            msg = f"""*{sig} SIGNAL {arrow}* 📈
`{p.replace('USDT','')}/USDT` • 5m
*Price:* `{pr:,.4f}`   {f'+{ch:.2f}%' if ch>0 else f'{ch:.2f}%'}
*UT Bot (key=2)* fired! 🔥"""
            tg(msg)
            print(f"{p} → {sig}")
            last_signal[p] = sig
    time.sleep(7)
