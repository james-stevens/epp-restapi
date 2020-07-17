#! /usr/bin/python3
# (c) Copyright 2019-2020, James Stevens ... see LICENSE for details
# Alternative license arrangements are possible, contact me for more information


import json
import xmltodict
import os
import sys
import syslog
import socket
import ssl
import time

from flask import Flask
from flask import request
from flask import Response

client_pem = "/opt/certkey.pem"

syslogFacility = syslog.LOG_LOCAL6

application = Flask("EPP/REST/API")
conn = None
idSeq = 0

EPP_PORT = 700

EPP_PKT_LEN_BYTES = 4
NETWORK_BYTE_ORDER = "big"


class Empty:
    pass


def hexId(i):
    return hex(int(i))[2:].upper()


def makeXML(cmd):
    global idSeq
    idSeq = idSeq + 1
    clTRID = "ID:" + hexId(time.time()) + "_" + hexId(
        os.getpid()) + "_" + hexId(idSeq)
    cmd["clTRID"] = clTRID
    xml = xmltodict.unparse({
        "epp": {
            "@xmlns": "urn:iana:xml:ns:epp",
            "@xmlns:xsi": "http://www.w3.org/2000/10/XMLSchema-instance",
            "@xsi:schemaLocation": "urn:iana:xml:ns:epp epp.xsd",
            "command": cmd
        }
    })
    return clTRID, ((EPP_PKT_LEN_BYTES + len(xml)).to_bytes(
        EPP_PKT_LEN_BYTES, NETWORK_BYTE_ORDER) + bytearray(xml, 'utf-8'))


def makeLogin(username, password):
    return {
        "login": {
            "clID": username,
            "pw": password,
            "options": {
                "version": "1.0",
                "lang": "en"
            },
            "svcs": {
                "contact:svc": {
                    "@xmlns:contact": "urn:iana:xml:ns:contact",
                    "@xsi:schemaLocation":
                    "urn:iana:xml:ns:contact contact.xsd"
                },
                "domain:svc": {
                    "@xmlns:domain": "urn:iana:xml:ns:domain",
                    "@xsi:schemaLocation": "urn:iana:xml:ns:domain domain.xsd"
                },
                "host:svc": {
                    "@xmlns:host": "urn:iana:xml:ns:host",
                    "@xsi:schemaLocation": "urn:iana:xml:ns:host host.xsd"
                }
            }
        },
    }


def jsonReply(conn, clTRID):
    l = int.from_bytes(conn.read(EPP_PKT_LEN_BYTES), NETWORK_BYTE_ORDER)
    js = xmltodict.parse(conn.read(l))
    ret = 9999
    if "epp" in js:
        js = js["epp"]

    if "@xmlns" in js:
        del js["@xmlns"]

    if "greeting" in js:
        return 1000, js

    if "response" in js:
        js = js["response"]

    if "result" in js and "@code" in js["result"]:
        ret = int(js["result"]["@code"])

    if "trID" in js and "clTRID" in js["trID"]:
        if js["trID"]["clTRID"] == clTRID:
            del js["trID"]
        else:
            ret = 9990

    return ret, js


def xmlReques(js):
    global conn
    clTRID, xml = makeXML(js)
    conn.send(xml)
    return jsonReply(conn, clTRID)


@application.route('/epp/api/v1.0/finish', methods=['GET'])
def closeEPP():
    ret, js = xmlReques({"logout": None})
    Response(js)
    syslog.syslog("Logout {}".format(ret))
    conn.close()
    conn = None
    ## want to terminate/exit here, not sure how from Flask


def firstDict(thisDict):
    for d in thisDict:
        return d

@application.route('/epp/api/v1.0/request', methods=['POST'])
def eppJSON():
    global conn
    t1 = firstDict(request.json)
    t2 = firstDict(request.json[t1])
    if t2[0] == "@":
        t2 = request.json[t1][t2]
    ret, js = xmlReques(request.json)
    syslog.syslog("User request: {} asked '{}/{}' -> {}".format(request.remote_addr,t1,t2,ret))
    return js



@application.before_first_request
def start_up_code():

    global conn

    syslog.openlog(logoption=syslog.LOG_PID, facility=syslogFacility)

    if ("EPP_SERVER" not in os.environ or "EPP_USERNAME" not in os.environ or "EPP_PASSWORD" not in os.environ):
        syslog.syslog(
            "ERROR: Either server, username or password has not been specified"
        )
    else:
        args = Empty()

        args.server = os.environ["EPP_SERVER"]
        args.username = os.environ["EPP_USERNAME"]
        args.password = os.environ["EPP_PASSWORD"]
        
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_cert_chain(client_pem)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = context.wrap_socket(s,
                                   server_side=False,
                                   server_hostname=args.server)

        conn.connect((args.server, EPP_PORT))

        ret, js = jsonReply(conn, None)
        syslog.syslog("Greeting {}".format(ret))

        ret, js = xmlReques(makeLogin(args.username, args.password))
        syslog.syslog("Login {}".format(ret))


if __name__ == "__main__":
        application.run()
