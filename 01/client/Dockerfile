FROM ghcr.io/maxotta/kiv-ds-docker:v0.9.1

RUN yum -q -y install python3
RUN pip3 install flask
RUN pip3 install requests

COPY ./ /opt/client

HEALTHCHECK CMD curl --fail http://localhost:5000/about || exit 1

CMD [ "/usr/bin/python3", "/opt/client/main.py" ]