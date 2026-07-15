import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DROP_PERCENT = -50

alerted_coins = set()


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id:CHAT_ID,
          "text":text
         }
    try:
        r = requests.post(url, data=data, timeout=15)
        print("Telegram:", r.status_code)
        print(r.text)
    except Exception as e:
        print("Telegram Error:", e)


def get_market():
    url = "https://www.ourbit.com/api/platform/spot/market/v2/tickers"

    try:
        response = requests.get(url, timeout=15)

        print("API Status:", response.status_code)

        if response.status_code != 200:
            print(response.text)
            return None

        return response.json()

    except Exception as e:
        print("API Error:", e)
        return None


def check_coins():

    data = get_market()

    if not data:
        return

    coins = data["data"]

    print("Coins:", len(coins))

    for coin in coins:

        try:

            symbol = coin["sb"]

            if symbol.startswith("~~"):
                continue

            change = float(coin["r8"]) * 100

            print(symbol, change)

            if change <=DROP_PERCENT:

                if symbol in alerted_coins:
                    continue

                alerted_coins.add(symbol)

                message = (
                    "🚨 ریزش شدید در Ourbit\n\n"
                    f"🪙 {symbol}\n"
                    f"📉 {change:.2f}%"
                )

                send_message(message)

        except Exception as e:
            print("Coin Error:", e)


print("Bot Started")


data=get_market()
print(data)
check_coins()

print("Finished")
