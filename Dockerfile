# (c) Copyright 2019-2020, James Stevens ... see LICENSE for details
# Alternative license arrangements are possible, contact me for more information

FROM alpine:3.16

RUN rmdir /run
RUN ln -s /dev/shm /run
RUN apk add nginx

RUN apk add python3 py-pip py3-flask py3-gunicorn py3-xmltodict py3-tz tzdata
RUN pip install apscheduler

RUN rmdir /tmp /var/lib/nginx/tmp /var/log/nginx 
RUN ln -s /dev/shm /tmp
RUN ln -s /dev/shm /var/lib/nginx/tmp
RUN ln -s /dev/shm /var/log/nginx
RUN ln -s /dev/shm /run/nginx

RUN mkdir /opt/keys
RUN chmod 700 /opt/keys
COPY certkey.pem /opt/keys
RUN chown -R nginx: /opt/keys

COPY myCA.pem /etc/ssl/private
RUN cat /etc/ssl/private/myCA.pem >> /etc/ssl/cert.pem

RUN rm -f /etc/inittab /etc/nginx/nginx.conf
RUN ln -s /run/inittab /etc/inittab
RUN ln -s /run/nginx.conf /etc/nginx/nginx.conf
COPY htpasswd /etc/nginx/htpasswd

COPY bin /usr/local/bin/
COPY epprest.py /opt/
RUN python3 -m compileall /opt/

CMD [ "/usr/local/bin/start" ]
