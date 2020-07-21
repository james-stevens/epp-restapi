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
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

import flask

client_pem = "/opt/certkey.pem"

syslogFacility = syslog.LOG_LOCAL6

application = flask.Flask("EPP/REST/API")
conn = None
idSeq = 0

EPP_PORT = 700

EPP_PKT_LEN_BYTES = 4
NETWORK_BYTE_ORDER = "big"

jobInterval = 0
if "EPP_KEEPALIVE" in os.environ:
    jobInterval = int(os.environ["EPP_KEEPALIVE"])


def keepAlive():
    jsonRequest({"hello":None},"keepAlive")


scheduler = None
if jobInterval > 0:
    scheduler = BackgroundScheduler(timezone=utc)
    scheduler.start(paused=True)
    job = scheduler.add_job(keepAlive, 'interval', minutes=jobInterval, id='keepAlive')


def gracefulExit():
    global conn
    if conn is None:
        return
    ret, js = xmlRequest({"logout": None})
    flask.Response(js)
    syslog.syslog("Logout {}".format(ret))
    conn.close()
    sys.exit(0)

atexit.register(gracefulExit)


class Empty:
    pass


def abort(err_no, message):
    response = flask.jsonify({'error': message})
    response.status_code = err_no
    return response



def hexId(i):
    return hex(int(i))[2:].upper()


def makeXML(cmd):
    global idSeq
    idSeq = idSeq + 1
    clTRID = "ID:" + hexId(time.time()) + "_" + hexId(
        os.getpid()) + "_" + hexId(idSeq)

    verb = "command"
    if "hello" in cmd:
        verb = "hello"
        cmd = None
    else:
        cmd["clTRID"] = clTRID

    xml = xmltodict.unparse({
        "epp": {
            "@xmlns": "urn:iana:xml:ns:epp",
            "@xmlns:xsi": "http://www.w3.org/2000/10/XMLSchema-instance",
            "@xsi:schemaLocation": "urn:iana:xml:ns:epp epp.xsd",
            verb: cmd
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
    buf = conn.recv(EPP_PKT_LEN_BYTES)
    if len(buf) == 0:
        return None, None
    l = int.from_bytes(buf, NETWORK_BYTE_ORDER)
    buf = conn.recv(l)
    if len(buf) == 0:
        return None, None
    js = xmltodict.parse(buf)
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



def xmlRequest(js):
    global conn
    clTRID, xml = makeXML(js)
    try:
        conn.sendall(xml)
        return jsonReply(conn, clTRID)
    except:
        return None, None



@application.route('/epp/api/v1.0/finish', methods=['GET'])
def closeEPP():
    gracefulExit()


def firstDict(thisDict):
    for d in thisDict:
        return d.lower()


def jsonRequest(in_js,addr):
    global conn
    global scheduler

    if conn is None:
        connectToEPP()
        if conn is None:
            return abort(400, "Failed to connect to EPP Server")

    t1 = firstDict(in_js)
    if t1 == "hello":
        t2="hello"
    else:
        t2 = firstDict(in_js[t1])
        if t2[0] == "@":
            t2 = in_js[t1][t2]

    if jobInterval > 0:
        scheduler.reschedule_job('keepAlive', trigger='interval', minutes=jobInterval)
        scheduler.resume()

    ret, js = xmlRequest(in_js)

    if ret is None or js is None:
        conn.close()
        conn = None
        connectToEPP()
        if conn is None:
            return abort(400, "Failed to connect to EPP Server")
        ret, js = xmlRequest(j)
        if ret is None or js is None:
            conn.close()
            conn = None
            return abort(400, "Lost connection to EPP Server")

    syslog.syslog("User request: {} asked '{}/{}' -> {}".format(addr,t1,t2,ret))

    return js



@application.route('/epp/api/v1.0/request', methods=['POST'])
def eppJSON():
    if flask.request.json is None:
        return abort(400, "No JSON data was POSTed")
    return jsonRequest(flask.request.json,flask.request.remote_addr)



def connectToEPP():

    global conn
    global scheduler

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

        syslog.syslog("Connecting to EPP Server: {}".format(args.server))
        try:
            conn.connect((args.server, EPP_PORT))
            conn.setblocking(True)
        except:
            conn.close()
            conn = None
            return

        ret, js = jsonReply(conn, None)
        syslog.syslog("Greeting {}".format(ret))

        ret, js = xmlRequest(makeLogin(args.username, args.password))
        syslog.syslog("Login {}".format(ret))

        scheduler.resume()



if __name__ == "__main__":
        application.run()
