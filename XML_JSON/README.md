# XML to JSON documentation

This directory gives examples of EPP requests in both XML and JSON format

## How XML is converted

At its most basic the XML is converted to JSON like this

    <xml-tag-name>some data value</xml-tag-name>

becomes

    { "xml-tag-name": "some data value" }

Where there are a series of XML tags of the same name, they become an array

        <domain:ns>
          <domain:hostObj>ns1.exmaple.net</domain:hostObj>
          <domain:hostObj>ns2.exmaple.net</domain:hostObj>
        </domain:ns>

becomes

        "domain:ns": {
            "domain:hostObj": [
                "ns1.testname.com",
                "ns1.testname.ac"
            ]
        },


paramters within an XML tag are treated like properties, with the prefix `@`

    <poll op="req"\>

becomes

    {
        "poll": {
            "@op" : "req"
            }
    }

if an XML tag encloses just data, as well as having parameters the enclosed data
is given the special property `#text`

    <domain:period unit="y">1</domain:period>

becomes

     "domain:period": {
        "@unit": "y",
        "#text": "1"
     },

