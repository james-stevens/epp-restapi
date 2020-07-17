#! /usr/bin/python3

import json
import xmltodict
import argparse
import os
import sys
import syslog
import socket
import ssl
import time

from flask import Flask
from flask import request
from flask import Response

client_pem = "certkey.pem"

syslogFacility = syslog.LOG_LOCAL6

app = Flask("EPP/REST/API")
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


@app.route('/epp/api/v1.0/finish', methods=['GET'])
def closeEPP():
    ret, js = xmlReques({"logout": None})
    Response(js)
    syslog.syslog("Logout {}".format(ret))
    conn.close()
    conn = None
    ## want to terminate/exit here, not sure how from Flask


@app.route('/epp/api/v1.0/request', methods=['POST'])
def eppJSON():
    global conn
    ret, js = xmlReques(request.json)
    syslog.syslog("User query: {}".format(ret))
    return js


if __name__ == "__main__":

    syslog.openlog(logoption=syslog.LOG_PID, facility=syslogFacility)

    args = Empty()
    args.server = os.environ["EPP_SERVER"]
    args.username = os.environ["EPP_USERNAME"]
    args.password = os.environ["EPP_PASSWORD"]

    if args.username is None or args.password is None or args.server is None:
        print(
            "ERROR: Either server, username or password has not been specified"
        )
        sys.exit(1)

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

    app.run()
