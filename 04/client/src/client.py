import os
from kazoo.client import KazooClient
from paho.mqtt import client as mqttclient
import random
from time import sleep

CLIENT_ID = random.randint(0, 100_000)
MQTT_PORT = 1883

cancellation_flag = False


def start_keeper() -> KazooClient:
    """
    Initialize connection to a keeper client
    """
    print("Starting keeper...")
    sleep(30)  # debug delay

    hosts = os.environ['KEEPER_HOSTS']
    client = KazooClient(hosts=hosts)
    client.start()
    print(f"Keeper client runs on: {{{hosts}}}.", flush=True)

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


def connect_to_mqtt(ip):
    """
    Connect to the MQTT broker
    """
    try:
        mqtt_client = mqttclient.Client(CLIENT_ID, reconnect_on_failure=False)
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
    print(f"{msg.payload.decode('utf-8')}", flush=True)
    # TODO any job


def do_mqtt_loop(keeper_client):
    """
    Query brokers from the keeper client, connect, and generate date / catch messages
    """
    print(f"Starting MQTT loop...", flush=True)
    sleep(10)  # init delay

    while not cancellation_flag:
        # Get and connect to a broker
        broker_ip = get_mqtt_broker_ip(keeper_client)
        mqtt_client = connect_to_mqtt(broker_ip)
        if mqtt_client is None:
            print(f"Failed broker connect ({broker_ip}).", flush=True)
            continue
        print(f"Connected broker: {broker_ip}", flush=True)

        # Set broker to loop forever
        mqtt_client.loop_forever()

        # Subscribe incoming messages
        mqtt_client.subscribe("ds/04/message")
        mqtt_client.on_message = event_mqtt_on_message

        # Random chance to generate a new message to send
        if random.random() < 0.2:
            print(f"Generating a new message...", flush=True)
            # Publish random number as the message in the MQTT client
            mqtt_client.publish("ds/04/message",
                                f"{CLIENT_ID}:"
                                f"{random.randint(0, 1000)}")
            # Sleep after send (random delay)
            sleep(random.randint(2, 20))

        sleep(1)
    print(f"MQTT has stopped!", flush=True)


def main():
    # Connect to Zookeeper
    keeper_client = start_keeper()

    # MQTT loop
    do_mqtt_loop(keeper_client)

    # Close the session to the keeper client
    keeper_client.stop()


if __name__ == "__main__":
    main()
