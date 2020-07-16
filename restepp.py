#! /usr/bin/python3

import json
import xmltodict
import argparse
import os
import sys
import socket
import ssl
import time

from flask import Flask
from flask import request
from flask import Response


client_cert = '/opt/pems/jrcs.net.pem'
client_key = '/opt/pems/jrcs.net.pem'

app = Flask("EPP/REST/API")
conn = None
clTRID = None
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
	global clTRID
	idSeq = idSeq + 1
	clTRID = "ID:" + hexId(time.time()) + "_" + hexId(os.getpid()) + "_" + hexId(idSeq)
	cmd["clTRID"] = clTRID
	xml = xmltodict.unparse( {
		"epp": {
			"@xmlns": "urn:iana:xml:ns:epp",
			"@xmlns:xsi": "http://www.w3.org/2000/10/XMLSchema-instance",
			"@xsi:schemaLocation": "urn:iana:xml:ns:epp epp.xsd",
			"command": cmd
			}
		})
	return (EPP_PKT_LEN_BYTES + len(xml)).to_bytes(EPP_PKT_LEN_BYTES,NETWORK_BYTE_ORDER) + bytearray(xml,'utf-8')



def makeLogin(username,password):
	return makeXML( {
		"login": {
			"clID": username,
			"pw": password,
			"options": {
				"version": "1.0",
				"lang": "en"
				},
			"svcs": {
				"contact:svc" : {
					"@xmlns:contact": "urn:iana:xml:ns:contact",
					"@xsi:schemaLocation": "urn:iana:xml:ns:contact contact.xsd"
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
		"clTRID": "4KabBYhZECWJWcpOIKsr"
		})
		


def jsonReply(conn):
	l = int.from_bytes(conn.read(EPP_PKT_LEN_BYTES),NETWORK_BYTE_ORDER)
	js = xmltodict.parse(conn.read(l))
	ret = 9999
	if "epp" in js:
		js = js["epp"]

	if "@xmlns" in js:
		del js["@xmlns"]

	if "greeting" in js:
		return 1000,js

	if "response" in js:
		r = js["response"]

		if "result" in r and "@code" in r["result"]:
			ret = int(js["response"]["result"]["@code"])

		if "trID" in r and "clTRID" in r["trID"]:
			if r["trID"]["clTRID"] == clTRID:
				del js["response"]["trID"]
			else:
				ret = 9990
		
	return ret, js



@app.route('/epp/api/v1.0/finish', methods=['GET'])
def closeEPP():
	global conn
	conn.send(makeXML({ "logout": None, "clTRID":"RQ-9375-1363779375950397" }))
	ret, js = jsonReply(conn)
	Response(js)
	print("===========> Logout",ret)
	conn.close()
	conn = None



@app.route('/epp/api/v1.0/request', methods=['POST'])
def eppJSON():
	global conn
	conn.send(makeXML(request.json))
	ret, js = jsonReply(conn)
	print("===========> User query:",ret)
	return js



if __name__ == "__main__":

	args = Empty()
	args.server = os.environ["EPP_SERVER"]
	args.username = os.environ["EPP_USERNAME"]
	args.password = os.environ["EPP_PASSWORD"]

	if args.username is None or args.password is None or args.server is None:
		print("ERROR: Either server, username or password has not been specified")
		sys.exit(1)

	context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
	context.load_cert_chain(certfile=client_cert, keyfile=client_key)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	conn = context.wrap_socket(s, server_side=False, server_hostname=args.server)

	conn.connect((args.server, EPP_PORT))

	ret, js = jsonReply(conn)
	print("===========> Greeting",ret)

	conn.send(makeLogin(args.username,args.password))
	ret, js = jsonReply(conn)
	print("===========> Login",ret)

	app.run()
