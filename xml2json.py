#! /usr/bin/python3
# (c) Copyright 2019-2020, James Stevens ... see LICENSE for details
# Alternative license arrangements possible, contact me for more information

# converts the XML file specified into JSON

import xmltodict
import json
import sys

with open(sys.argv[1]) as fd:
    print(json.dumps(xmltodict.parse(fd.read()), indent=3))
