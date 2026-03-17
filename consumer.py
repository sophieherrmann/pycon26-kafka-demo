"""
Kafka Consumer — reads crypto price updates from the 'prices' topic.

Usage:
    python consumer.py                  # default group "price-viewer"
    python consumer.py --group alerts   # custom group "alerts"
"""

import argparse
import json
import signal

from confluent_kafka import Consumer, KafkaError

TOPIC = "prices"
BROKER = "localhost:9092"

running = True


def shutdown(signum, frame):
    global running
    running = False


def main():
    parser = argparse.ArgumentParser(description="Kafka price consumer")
    parser.add_argument("--group", default="price-viewer", help="Consumer group ID (default: price-viewer)")
    args = parser.parse_args()
    group_id = args.group

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    consumer = Consumer(
        {
            "bootstrap.servers": BROKER,
            "group.id": group_id,
            "auto.offset.reset": "latest",
            "enable.auto.commit": True,
        }
    )
    consumer.subscribe([TOPIC])
    print(f"Consuming from '{TOPIC}' (group={group_id}) — Ctrl+C to stop\n")

    try:
        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                print(f"Error: {msg.error()}")
                continue

            data = json.loads(msg.value().decode())
            print(
                f"[partition {msg.partition():>2} | offset {msg.offset():>5}]  "
                f"{data['asset']}/EUR = {data['price']:>12.6f}  "
                f"@ {data['timestamp']}"
            )
    finally:
        print("\nClosing consumer...")
        consumer.close()


if __name__ == "__main__":
    main()
