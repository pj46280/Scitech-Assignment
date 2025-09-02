import paho.mqtt.client as mqtt
import json
import random
import time
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("iot_pipeline.log"),
        logging.StreamHandler()
    ]
)

BROKER = "localhost"  
PORT = 1883
TOPIC = "scitech/sensors"

OUTPUT_FILE = "sensor_data.json"
received_data = []


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker")
        client.subscribe(TOPIC)
    else:
        logging.error(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    global received_data
    payload = msg.payload.decode()
    logging.info(f"Received: {payload}")

    try:
        data = json.loads(payload)
        received_data.append(data)

        with open(OUTPUT_FILE, "w") as f:
            json.dump(received_data, f, indent=4)

    except Exception as e:
        logging.error(f"Error decoding JSON: {e}")


def generate_sensor_data():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "temperature": round(random.uniform(20, 35), 2), 
        "rh": round(random.uniform(30, 80), 2)         
    }


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
    except Exception as e:
        logging.error(f"Could not connect to broker: {e}")
        return

    client.loop_start()

    try:
        while True:
            data = generate_sensor_data()
            payload = json.dumps(data)
            client.publish(TOPIC, payload)
            logging.info(f"Published: {payload}")
            time.sleep(300)

    except KeyboardInterrupt:
        logging.warning("Stopped by user.")
    finally:
        client.loop_stop()
        client.disconnect()
        logging.info("MQTT client disconnected.")


if __name__ == "__main__":
    main()
