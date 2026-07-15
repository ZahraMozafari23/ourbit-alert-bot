import os
import json
import time
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# درصد ریزش موردنظر
DROP_PERCENT = 100

# هر 5 دقیقه اجرا می‌شود
CHECK_INTERVAL = 300

# نگهداری 12 رکورد = حدود 1 ساعت
MAX_HISTORY = 12

# جلوگیری از هشدار تکراری
alerted_coins = set()


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=15
        )
            print("Telegram Status:", response.status_code)
            print(response.text)
    except Exception as e:
        print("Telegram Error:", e)


def load_prices():
    try:
        with open("prices.json", "r") as f:
            return json.load(f)
    except:
        return {}


def save_prices(data):
    with open("prices.json", "w") as f:
        json.dump(data, f, indent=2)


def get_market():

    url = "https://www.ourbit.com/api/platform/spot/market/v2/tickers"

    try:
        response = requests.get(url, timeout=20)

        print("API Status:", response.status_code)

        if response.status_code != 200:
            print(response.text)
            return None

        return response.json()

    except Exception as e:
        print("API Error:", e)
        return None


def update_history(history, symbol, price):

    if symbol not in history:
        history[symbol] = []

    history[symbol].append({
        "time": int(time.time()),
        "price": price
    })

    if len(history[symbol]) > MAX_HISTORY:
        history[symbol] = history[symbol][-MAX_HISTORY:]
        
def check_coins():

    history = load_prices()

    data = get_market()

    if not data:
        return

    coins = data["data"]

    print("Coins:", len(coins))

    for coin in coins:

        try:

            symbol = coin["sb"]

            # حذف بازارهای غیرعادی
            if symbol.startswith("~~"):
                continue

            price = float(coin["c"])

            # اگر قبلاً سابقه داشته باشد
            if symbol in history and len(history[symbol]) >= MAX_HISTORY:

                current_time = int(time.time())

                old_record = None

                for item in history[symbol]:
                    if current_time - item["time"] >= 3600:
                       old_record = item
                       break
                if old_record:
                    old_price = old_record["price"]
                else:
                     old_price = history[symbol][0]["price"]
  
                
                if old_price > 0:

                    change = ((price - old_price) / old_price) * 100

                    print(symbol, f"{change:.2f}%")

                    if True:

                        if symbol not in alerted_coins:

                            alerted_coins.add(symbol)

                            message = (
                                "🚨 هشدار ریزش شدید\n\n"
                                f"🪙 {symbol}\n"
                                f"📉 افت: {change:.2f}%\n\n"
                                f"💵 یک ساعت قبل: {old_price}\n"
                                f"💵 الان: {price}"
                            )

                            send_message(message)

                    else:
                        # اگر دوباره عادی شد اجازه هشدار بعدی بده
                        if symbol in alerted_coins:
                            alerted_coins.remove(symbol)

            # ذخیره قیمت جدید
            update_history(history, symbol, price)

        except Exception as e:
            print("Coin Error:", symbol, e)

    save_prices(history)

    print("History Saved")


print("Bot Started")

check_coins()

print("Finished")
