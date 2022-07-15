# (c) Copyright 2019-2022, James Stevens ... see LICENSE for details
# Alternative license arrangements are possible, contact me for more information

FROM gunicorn-flask

RUN apk add py-pip py3-xmltodict py3-tz tzdata
RUN pip install apscheduler

RUN mkdir /opt/keys
RUN chmod 700 /opt/keys
COPY certkey.pem /opt/keys/client.pem

COPY nginx_login.conf /etc/nginx
COPY htpasswd /etc/nginx/htpasswd

COPY epprest.py wsgi.py /opt/python/
RUN python3 -m compileall /opt/python
