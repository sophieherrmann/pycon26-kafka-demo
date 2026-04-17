"""
Kafka Producer — sends random crypto price updates to the 'prices' topic.

Usage:
    python producer.py
"""

import json
import random
import time
from datetime import datetime, timezone

from confluent_kafka import Producer

TOPIC = "prices"
BROKER = "localhost:9092"

ASSETS = {
    "BTC": 84_000.0,
    "ETH": 1_900.0,
    "SOL": 130.0,
    "DOGE": 0.17,
    "XRP": 1.15,
    "VSN": 0.048,
    "PEPE": 0.000003671,
}


def make_price_message(asset: str, base_price: float) -> dict:
    jitter = random.uniform(-0.02, 0.02)  # +-2%
    price = round(base_price * (1 + jitter), 6)
    return {
        "asset": asset,
        "currency": "EUR",
        "price": price,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def delivery_report(err, msg):
    if err:
        print(f"  FAILED: {err}")
    else:
        print(f"  -> {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")


def main():
    producer = Producer({"bootstrap.servers": BROKER})
    print(f"Producing price updates to '{TOPIC}' — Ctrl+C to stop\n")

    try:
        while True:
            asset = random.choice(list(ASSETS))
            message = make_price_message(asset, ASSETS[asset])
            payload = json.dumps(message)

            print(f"Sending: {message['asset']}/EUR = {message['price']}")
            producer.produce(
                TOPIC,
                key=asset,
                value=payload.encode(),
                callback=delivery_report,
            )
            producer.poll(0)  # trigger delivery callbacks
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping producer...")
    finally:
        producer.flush(timeout=5)


if __name__ == "__main__":
    main()
