FROM ghcr.io/maxotta/kiv-ds-docker:latest

RUN yum -y update
RUN sudo yum -q -y install python3
RUN pip3 install kazoo
RUN pip3 install paho-mqtt
RUN sudo yum -y install epel-release
RUN sudo yum -y install mosquitto
RUN sudo yum -q -y install nc

RUN rm -f /mosquitto/config/mosquitto.conf
COPY mosquitto.conf /mosquitto/config/mosquitto.conf

EXPOSE 1883 9001

COPY docker-entrypoint.sh /usr/bin/docker-entrypoint.sh
RUN chmod a+x /usr/bin/docker-entrypoint.sh

COPY src /opt/broker

HEALTHCHECK --interval=10s --timeout=10s --start-period=30s --retries=3 CMD nc -z localhost 22 && nc -u -z localhost 12345 && mosquitto_sub -t '$SYS/#' -C 1

CMD /usr/bin/docker-entrypoint.sh