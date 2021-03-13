import argparse
import json
import threading
import time

import requests
import websocket
from rich.live import Live
from rich.table import Table


ONE_BTC_AUD = json.loads(requests.get("https://blockchain.info/ticker").content)["AUD"]["15m"]
WS_LIFE = 10 # program life in seconds

table = Table(show_lines=True)
table.add_column("timestamp", overflow="fold", justify="center")
table.add_column("hash", overflow="fold", min_width=32, max_width=32) # hash length 64
table.add_column("from_addr", overflow="fold")
table.add_column("from_amt", overflow="fold")
table.add_column("to_addr", overflow="fold")
table.add_column("to_amt", overflow="fold")
table.add_column("est_aud", overflow="fold")

live = Live(table, vertical_overflow="ellipsis", refresh_per_second=4)

def on_message(ws, message):
    message = json.loads(message)

    timestamp = time.strftime("%Y-%m-%d\n%H:%M:%S", time.localtime(message["x"]["time"]))
    hash = message["x"]["hash"]
    from_address = [input["prev_out"]["addr"] for input in message["x"]["inputs"]]
    from_amt = [str(int(input["prev_out"]["value"]) / 100000000) for input in message["x"]["inputs"]]
    to_address = [output["addr"] for output in message["x"]["out"]]
    to_amt = [str(int(output["value"]) / 100000000) for output in message["x"]["out"]]
    est_aud = list(map(lambda x: float(x) * ONE_BTC_AUD, to_amt))

    table.add_row(timestamp, hash, "\n".join(from_address), "\n".join(from_amt), "\n".join(to_address), "\n".join(to_amt), "\n".join(map(lambda x: "${:,.2f}".format(x), est_aud)))

def on_error(ws, error):
    print(error)

def on_open(ws):
    ws.send('{"op":"unconfirmed_sub"}')

def close_ws(ws):
    time.sleep(WS_LIFE)
    ws.close()

def main():
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "wss://ws.blockchain.info/inv",
        on_message = on_message,
        on_error = on_error,
        on_open=on_open
    )

    live.start()

    thread = threading.Thread(target=close_ws, args=(ws,))
    thread.daemon = True
    thread.start()

    ws.run_forever()

if __name__ == "__main__":
    main()
