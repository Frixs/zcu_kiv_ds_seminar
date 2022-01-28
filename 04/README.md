# KIV/DS #04
*To run the example, use the command: `vagrant up`*

<p align="center">
    <img src="../03/ds03.png" alt="Chart DS 03" style="text-align:center;">
</p>


## Nodes
3 types of nodes: Keeper (ZooKeeper), MQTT Broker, Client

- **ZooKeeper**
    - Information about all available nodes

- **MQTT Broker**
    -   represented by Mosquitto broker
    -   python script defines dispatching of the broker
        - registers and keeps evidence of all active brokers
        - forwarding system -> message is not forwarded with assigned tag in the message
        - exiting session ends up with exit code -1
        - once message is caught, it is distributed to the MQTT broker

- **Client**
    - Connects to the random selected broker node from the given selection


## About

Clients listen to incoming messages with a chance 50% to send a new message by itself. If the client disconnects, it turns off.

Each item in the example has healthcheck script (`health-check.sh`).  
ZooKeeper runs on port `5555` for verifing health.  
`mosquitto_sub -t '$SYS/#' -C 1` to check that MQTT is responding.
