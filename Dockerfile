# (c) Copyright 2019-2020, James Stevens ... see LICENSE for details
# Alternative license arrangements are possible, contact me for more information

FROM alpine

RUN rmdir /tmp
RUN ln -s /dev/shm /tmp
RUN ln -s /dev/shm /ram

RUN apk add python3
RUN apk add py-pip
RUN apk add nginx
RUN apk add bind-tools

RUN pip install --upgrade pip
RUN pip install gunicorn
RUN pip install Flask
RUN pip install xmltodict

RUN rmdir /var/lib/nginx/tmp /var/log/nginx 
RUN ln -s /dev/shm /var/lib/nginx/tmp
RUN ln -s /dev/shm /var/log/nginx
RUN ln -s /dev/shm /run/nginx

COPY start_epprest start_nginx epprest.py /opt/
COPY certkey.pem nginx_ssl.conf /etc/nginx/
COPY inittab /etc/
RUN ln -s /etc/nginx/certkey.pem /opt/certkey.pem

RUN python3 -m compileall /opt/
