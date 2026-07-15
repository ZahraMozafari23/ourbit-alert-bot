import os
import json
import time
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHAT_ID_2 = os.getenv("CHAT_ID_2")

# درصد ریزش موردنظر
DROP_PERCENT = 20

# فاصله زمانی هدف (یک ساعت)
TARGET_TIME = 3600

# نگهداری حداکثر تاریخچه
MAX_HISTORY = 20


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    for chat_id in [CHAT_ID, CHAT_ID_2]:
        print("sending to:" , chat_id)

        if not chat_id:
            continue

        try:
            requests.post(
                url,
                data={
                    "chat_id": chat_id,
                    "text": text
                },
                timeout=15
            )

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

        response = requests.get(
            url,
            timeout=20
        )

        print("API Status:", response.status_code)

        if response.status_code != 200:
            print(response.text)
            return None

        return response.json()

    except Exception as e:

        print("API Error:", e)
        return None


def add_price(history, symbol, price):

    if symbol not in history:
        history[symbol] = []

    history[symbol].append(
        {
            "time": int(time.time()),
            "price": price
        }
    )

    # فقط تاریخچه اخیر نگه داشته شود
    if len(history[symbol]) > MAX_HISTORY:
        history[symbol] = history[symbol][-MAX_HISTORY:]
def find_old_price(records):

    now = int(time.time())

    old_record = None
    smallest_difference = None

    for item in records:

        diff = now - item["time"]

        # نزدیک‌ترین رکورد به یک ساعت قبل
        if diff >= TARGET_TIME:

            if smallest_difference is None or diff < smallest_difference:
                smallest_difference = diff
                old_record = item

    if old_record:
        return old_record["price"]

    return None



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

            # همه ارزها بررسی شوند
            price = float(coin["c"])


            # اگر برای این ارز تاریخچه داریم
            if symbol in history:

                old_price = find_old_price(history[symbol])


                if old_price:

                    if old_price > 0:

                        change = ((price - old_price) / old_price) * 100

                        print(symbol, f"{change:.2f}%")

                        if change <= DROP_PERCENT:

                            message = (
                                "🚨 هشدار ریزش شدید\n\n"
                                f"🪙 {symbol}\n"
                                f"📉 افت: {change:.2f}%\n\n"
                                f"💵 یک ساعت قبل: {old_price}\n"
                                f"💵 الان: {price}"
                            )

                            send_message(message)



            # ذخیره قیمت جدید
            add_price(
                history,
                symbol,
                price
            )


        except Exception as e:

            print("Coin Error:", e)



    save_prices(history)

    print("History Saved")



print("Bot Started")

check_coins()

print("Finished")
