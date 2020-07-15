#! /usr/bin/python3

import json
import xmltodict
import argparse
import os
import sys
import socket
import ssl

EPP_PORT = 700

EPP_PKT_LEN_BYTES = 4
NETWORK_BYTE_ORDER = "big"

def makeXML(cmd):
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
	return xmltodict.parse(conn.read(l))



parser = argparse.ArgumentParser(description='EPP REST/API Proxy')
parser.add_argument("-s", '--server', help='EPP Server')
parser.add_argument("-u", '--username', help='Username')
parser.add_argument("-p", '--password', help='Password')
parser.add_argument("-j", '--json', help='JSON to convert to XML')
args = parser.parse_args()

if args.server is None and "EPP_SERVER" in os.environ:
	args.server = os.environ["EPP_SERVER"]

if args.username is None and "EPP_USERNAME" in os.environ:
	args.username = os.environ["EPP_USERNAME"]

if args.password is None and "EPP_PASSWORD" in os.environ:
	args.password = os.environ["EPP_PASSWORD"]

if args.username is None or args.password is None or args.server is None:
	print("ERROR: Either server, username or password has not been specified")
	sys.exit(1)


# print(makeXML({"poll": { "@op":"req" }, "clTRID":"RQ-9375-1363779375950397" }))

server_sni_hostname = 'epp.jrcs.net'
client_cert = '/opt/pems/jrcs.net.pem'
client_key = '/opt/pems/jrcs.net.pem'

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(s, server_side=False, server_hostname=server_sni_hostname)

conn.connect((args.server, EPP_PORT))

## print("SSL established. Peer: {}".format(conn.getpeercert()))

print("===========> Sending: Login")
conn.send(makeLogin(args.username,args.password))
print(json.dumps(jsonReply(conn),indent=4))

print("===========> Sending: Poll")
conn.send(makeXML({ "poll": { "@op":"req" }, "clTRID":"RQ-9375-1363779375950397" }))
print(json.dumps(jsonReply(conn),indent=4))

print("===========> Sending: Logout")
conn.send(makeXML({ "logout": None, "clTRID":"RQ-9375-1363779375950397" }))
print(json.dumps(jsonReply(conn),indent=4))

print("Closing connection")
conn.close()

