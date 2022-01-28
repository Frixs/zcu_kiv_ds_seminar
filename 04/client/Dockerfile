#
# Zookeeper client node demo container image
#

FROM ghcr.io/maxotta/kiv-ds-docker:latest

RUN yum -q -y install python3
RUN pip3 install kazoo
RUN pip3 install paho-mqtt

COPY src /opt/zk/client
RUN chmod a+rwx /opt/zk/client/health-check.sh

HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 CMD /opt/zk/client/health-check.sh || exit 1

CMD python3 -u /opt/zk/client/client.py

# EOF