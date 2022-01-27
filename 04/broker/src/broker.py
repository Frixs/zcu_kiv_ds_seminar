import os
from kazoo.client import KazooClient
from paho.mqtt import client as mqttclient
import socket
import threading
from time import sleep

MQTT_PORT = 1883
DISPATCHER_PORT = 12345
TAG_FORWARD = "::FW"


def start_keeper() -> KazooClient:
    """
    Initialize connection to a keeper client
    """
    print("Connecting to a Keeper...", flush=True)
    sleep(15)  # debug delay

    hosts = os.environ['KEEPER_HOSTS']

    client = KazooClient(hosts=hosts)
    client.start()
    if client.connected:
        print(f"Successfully connected to the Keeper '{client.client_id}'!", flush=True)

    return client


def register_broker(keeper_client):
    """
    Register the broker in the keeper
    """
    ip = os.environ["IP"]  # current
    cluster_name = os.environ["CLUSTER_NAME"]
    keeper_client.create(f"/cluster/{cluster_name}/node", makepath=True, ephemeral=True, sequence=True,
                         value=ip.encode("utf-8"))
    print(f"Successfully registered the broker {ip} in the Keeper!", flush=True)


def start_mqtt() -> mqttclient.Client:
    """
    Initialize connection to MQTT client
    """
    client = mqttclient.Client("mqtt")
    client.on_connect = event_on_mqtt_connect
    client.connect(os.environ["IP"], port=MQTT_PORT)
    return client


def broadcast_message(topic, content):
    """
    Broadcast a message to all other dispatchers
    """
    print(f"\tBroadcast message '{topic}'...", flush=True)

    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    soc.sendto(f"{topic}|{content}".encode("utf-8"), ("255.255.255.255", DISPATCHER_PORT))


def event_on_mqtt_connect(client, userdata, flags, rc):
    """
    On connect MQTT client to broker.
    """
    if rc == 0:
        client.subscribe("#")
        client.on_message = event_mqtt_on_message
    else:
        print("Connection to MQTT broker failed!", flush=True)
        exit(-1)


def event_mqtt_on_message(msg):
    """
    On receive MQTT message
    """
    topic = msg.topic
    content = msg.payload.decode("utf-8")

    print(f"MQTT received: {{{topic}: {content}}}", flush=True)

    # If forwarded message...
    if TAG_FORWARD in content:
        print("-> Forward Message (dropping...)", flush=True)
        return

    # Otherwise...
    else:
        broadcast_message(topic, content)


def do_receive_message(client):
    """
    On receive any message (from other dispatchers) thread loop
    """
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.bind(("", DISPATCHER_PORT))

    while True:
        data = soc.recvfrom(1024)

        my_ip = socket.gethostbyname(socket.gethostname())
        # If external source...
        if my_ip == data[1][0]:
            continue

        content = data[0].decode("utf-8")

        # Check for the separator
        if "|" not in content:
            continue
        # Otherwise, message is formatted...
        # Separate message into corresponding parts
        msg_parts = content.split("|")
        topic = msg_parts[0]
        content = f"{TAG_FORWARD}{msg_parts[1]}"
        # Publish
        client.publish(topic, content.encode("utf-8"))


def main():
    # Inits
    keeper_client = start_keeper()
    mqtt_client = start_mqtt()

    # Register broker
    register_broker(keeper_client)

    # Start receiving message
    threading.Thread(target=do_receive_message, daemon=True, args=(mqtt_client,)).start()

    # Start MQTT
    mqtt_client.loop_forever()


if __name__ == "__main__":
    main()
