import os
import random
import time
from time import sleep
from typing import Optional

from kazoo.client import KazooClient
from paho.mqtt import client as mqttclient


cancellation_flag = False
random.seed(time.time() * 1000)  # seed gen
ID = f"c-{random.randint(0, 100_000)}"  # Random ID for the current node
MQTT_PORT = 1883


def start_keeper() -> KazooClient:
    """
    Initialize connection to a keeper client
    """
    print("Starting keeper...")

    hosts = os.environ['ZOO_SERVERS']

    sleep(15)  # debug delay
    client = KazooClient(hosts=hosts)
    client.start()
    print(f"Keeper client runs on: [{hosts}].", flush=True)

    return client


def get_mqtt_broker_ip(keeper_client) -> str:
    """
    Take list of all MQTT brokers and choose random one.
    """
    cluster_name = os.environ["CLUSTER_NAME"]

    # Get the list of all brokers
    brokers = keeper_client.get_children(f"/cluster/{cluster_name}")
    if len(brokers) <= 0:
        print("Error! No MQTT brokers!", flush=True)
        exit(-1)

    # Choose a random broker and retrieve its IP
    broker = random.choice(brokers)
    return keeper_client.get(f"/cluster/{cluster_name}/{broker}")[0].decode("utf-8")


def try_generate_message(client):
    """
    Try to generate new message
    """
    # Random chance to generate a new message to send
    if random.random() > 0.5:
        print(f"Generating a new message...", flush=True)
        # Publish random number as the message in the MQTT client
        client.publish("ds/04/message",
                       f"{ID}:"
                       f"{random.randint(0, 1000)}")
        # Sleep after send (random delay)
        sleep(random.randint(2, 20))


def connect_to_mqtt(ip) -> Optional[mqttclient.Client]:
    """
    Connect to the MQTT broker
    """
    try:
        mqtt_client = mqttclient.Client(ID, reconnect_on_failure=False)
        mqtt_client.on_connect = event_mqtt_on_connect
        mqtt_client.on_disconnect = event_mqtt_on_disconnect
        # Connect
        mqtt_client.connect(ip, MQTT_PORT)
        return mqtt_client

    except Exception:
        # If failed to connect...
        return None


def event_mqtt_on_connect(client, userdata, flags, rc):
    """
    On MQTT connect
    """
    global cancellation_flag

    if rc == 0:
        cancellation_flag = False
    else:
        cancellation_flag = True


def event_mqtt_on_disconnect(client, userdata, rc):
    """
    On MQTT disconnect
    """
    global cancellation_flag
    cancellation_flag = True
    print(f"Connection to the broker has benn lost!")


def event_mqtt_on_message(client, userdata, msg):
    """
    On message MQTT event hadnling
    """
    # Print message of payload
    print(f"MESSAGE: {msg.payload.decode('utf-8')}", flush=True)

    try_generate_message(client)


def client_loop(keeper_client):
    """
    Query brokers from the keeper client, connect, and generate date / catch messages
    """
    print(f"Starting MQTT loop...", flush=True)
    sleep(10)  # init delay
    global cancellation_flag

    while not cancellation_flag:
        sleep(5)  # TODO R
        cancellation_flag = False
        # Get and connect to a broker
        broker_ip = get_mqtt_broker_ip(keeper_client)
        mqtt_client = connect_to_mqtt(broker_ip)
        if mqtt_client is None:
            print(f"Failed broker connect ({broker_ip}).", flush=True)
            continue
        print(f"Connected broker: {broker_ip}", flush=True)

        try_generate_message(mqtt_client)

        print(f"Subscribing...", flush=True)
        # Subscribe incoming messages
        mqtt_client.subscribe("ds/04/message")
        mqtt_client.on_message = event_mqtt_on_message
        # Set broker to loop forever
        mqtt_client.loop_forever()

        sleep(1)

    print(f"Stopping MQTT loop...", flush=True)


def main():
    # Connect to Keeper client
    keeper_client = start_keeper()

    # Main loop (MQTT)
    client_loop(keeper_client)

    # Close the session of the keeper client
    keeper_client.stop()


main()
