import json
import threading
import time

import requests
import websocket
from rich.live import Live
from rich.table import Table


ONE_BTC_AUD = json.loads(requests.get("https://blockchain.info/ticker").content)["AUD"]["15m"]
PROG_LIFE = 10 # program life in seconds

table = Table(show_lines=True)
table.add_column("timestamp")
table.add_column("hash")
table.add_column("from_addr")
table.add_column("from_amt")
table.add_column("to_addr")
table.add_column("to_amt")
table.add_column("est_aud")

live = Live(table, vertical_overflow="visible", refresh_per_second=4)
live.start()

def on_message(ws, message):
    message = json.loads(message)

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(message["x"]["time"]))
    hash = message["x"]["hash"]
    from_addresses = [input["prev_out"]["addr"] for input in message["x"]["inputs"]]
    from_amts = [str(int(input["prev_out"]["value"]) / 100000000) for input in message["x"]["inputs"]]
    to_addresses = [output["addr"] for output in message["x"]["out"]]
    to_amts = [str(int(output["value"]) / 100000000) for output in message["x"]["out"]]
    est_auds = list(map(lambda x: str(float(x) * ONE_BTC_AUD), to_amts))

    table.add_row(timestamp, hash, "\n".join(from_addresses), "\n".join(from_amts), "\n".join(to_addresses), "\n".join(to_amts), "\n".join(est_auds))

def on_error(ws, error):
    print(error)

def on_open(ws):
    ws.send('{"op":"unconfirmed_sub"}')

def close_ws(ws):
    time.sleep(PROG_LIFE)
    ws.close()

def main():
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "wss://ws.blockchain.info/inv",
        on_message = on_message,
        on_error = on_error,
        on_open=on_open
    )

    threading.Thread(target=close_ws, args=(ws,)).start()
    ws.run_forever()

if __name__ == "__main__":
    main()
