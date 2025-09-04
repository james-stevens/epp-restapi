# (c) Copyright 2019-2022, James Stevens ... see LICENSE for details
# Alternative license arrangements are possible, contact me for more information

FROM gunicorn-flask

RUN apk add py-pip py3-xmltodict py3-tz tzdata py3-apscheduler

RUN mkdir /opt/keys
RUN chmod 700 /opt/keys
COPY certkey.pem /opt/keys/client.pem

COPY htpasswd /etc/nginx/htpasswd

COPY python /opt/python/
RUN python3 -m compileall /opt/python
