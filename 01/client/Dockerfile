FROM ghcr.io/maxotta/kiv-ds-docker:v0.9.1

RUN yum -q -y install python3
RUN pip3 install flask
RUN pip3 install requests

COPY ./ /opt/client

CMD [ "/usr/bin/python3", "/opt/client/main.py" ]