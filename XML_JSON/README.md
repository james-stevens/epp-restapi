# XML to JSON documentation

This directory gives examples of EPP requests in both XML and JSON format

The utility `xml2json.py <file>` is provided to allow you to convert EPP's XML 
into JSON to see what it will look like.

This is document set is not intended as a comprehensive documentation of the EPP object format, but
simple to cover enough scenarios so you can understand how the EPP/XML is mapped into JSON.


## How XML is converted

At its most basic the XML is converted to JSON like this

    <xml-tag-name>some data value</xml-tag-name>

becomes

    { "xml-tag-name": "some data value" }

With the hierarchy of relationship represented as you would expect.

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


parameters within an XML tag are treated like properties, with the prefix `@`

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

