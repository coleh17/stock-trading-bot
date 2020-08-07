import requests
import json
import websocket
from config import *

BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
POSITIONS_URL = "{}/v2/positions".format(BASE_URL)
HEADERS = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": SECRET_KEY}


def on_open(ws):
    print("opened")
    auth_data = {
        "action": "authenticate",
        "data": {"key_id": API_KEY, "secret_key": SECRET_KEY}
    }

    ws.send(json.dumps(auth_data))
    listen_message = {"action": "listen", "data": {"streams": ["AM.TSLA", "AM.SPY", "AM.AAPL", "AM.MSFT", "AM.DIS", "AM.AMD", "AM.PLUG", "AM.GE", "AM.APPS", "AM.F", "AM.UPS", "AM.BAC"]}}
    
    ws.send(json.dumps(listen_message))


def on_close(ws):
    print("closed connection")


def on_message(ws, message):
    #print(message)
    data = json.loads(message)
    print("checking {}".format(data["data"]["T"]))
    #print("open: {}\nclose:{}".format(float(data["data"]["o"]), float(data["data"]["c"])))

    if float(data["data"]["c"]) < float(data["data"]["o"]):
        response = create_order(data["data"]["T"], 10, "buy", "market", "gtc")
        # prfloat(response)
        print("++ BOUGHT 10 {}".format(data["data"]["T"]))

    elif float(data["data"]["c"]) > float(data["data"]["o"]):
        r = requests.get("https://paper-api.alpaca.markets/v2/positions/{}".format(data["data"]["T"]), headers=HEADERS)
        x = json.loads(r.content)

        if int(x["qty"]) > 0:
            response = create_order(data["data"]["T"], 10, "sell", "market", "gtc")
            # print(response)
            print("-- SOLD 10 {}".format(data["data"]["T"]))

    else:
        print("passing")

    # try:
    #     if data["stream"] != "authorization" and data["stream"] != "listening":
    #         print(data["data"]["T"])
    #         print("Close: ", data["data"]["c"])
    #         print("Open: ", data["data"]["o"])

    #         # if data["data"]["c"] > data["data"]["o"] and data["data"]["o"] - data["data"]["l"] > 0.1:
    #         if int(data["data"]["c"]) > int(data["data"]["o"]):
    #             print('Buying on Doji!')
    #         else:
    #             print('NOT BUYING')
    #             #if (bar.open > bar.close) and (bar.open - bar.low < (bar.open * 0.01)):
    # except:
    #     print("an error has occured")



def get_account():
    r = requests.get(ACCOUNT_URL, headers=HEADERS)
    return json.loads(r.content)

def create_order(symbol, qty, side, type, time_in_force):
    data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": type,
        "time_in_force": time_in_force
    }
    r = requests.post(ORDERS_URL, json=data, headers=HEADERS)
    return json.loads(r.content)

socket = "wss://data.alpaca.markets/stream"

ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)
ws.run_forever()