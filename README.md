# Kafka Producer/Consumer Demo

Minimal live demo: a single Kafka broker with a Python producer sending random crypto price updates and a consumer reading them.

## Prerequisites

- Docker & Docker Compose
- Python 3.12+

## Quick Start

### 1. Start the broker + UI

```bash
cd demo
docker compose up -d
```

Wait a few seconds for the broker to become healthy. The **Kafka UI** is at [http://localhost:8080](http://localhost:8080).

### 2. Create a virtual environment and install dependencies

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **Note:** `confluent-kafka` includes a C extension and ships prebuilt wheels for Python 3.12 and 3.13 on macOS/Linux. If `pip install` fails with a compiler error, make sure `librdkafka` is installed (`brew install librdkafka` on macOS).

### 3. Run the consumer (Terminal 1)

```bash
source .venv/bin/activate
python consumer.py
```

### 4. Run the producer (Terminal 2)

```bash
source .venv/bin/activate
python producer.py
```

You'll see price messages flowing from producer → broker → consumer. Open the Kafka UI to inspect the `prices` topic, partitions, and consumer group.

### Multiple consumer groups (fan-out)

Run consumers with different `--group` values to show that each group independently receives all messages:

```bash
# Terminal A
python consumer.py --group price-viewer

# Terminal B
python consumer.py --group alerts
```

Both consumers will receive every message. Check the Kafka UI to see the two consumer groups and their offsets.

### Changing the number of partitions

The default partition count for auto-created topics is set via `KAFKA_NUM_PARTITIONS` in `docker-compose.yml` (currently 3). To change it, update the value and recreate the broker:

```bash
docker compose down
# edit KAFKA_NUM_PARTITIONS in docker-compose.yml
docker compose up -d
```

With multiple partitions you can demo how messages are distributed across partitions and how consumers in the same group split the work.

### 5. Tear down

```bash
docker compose down
```

## What's in the box

| File | Purpose |
|---|---|
| `docker-compose.yml` | Single Kafka broker (KRaft mode, Apache Kafka 3.9) + Kafka UI |
| `producer.py` | Sends random BTC/ETH/SOL/DOGE price messages (1/sec) |
| `consumer.py` | Reads and prints price messages from the `prices` topic |
| `requirements.txt` | `confluent-kafka` Python client |

