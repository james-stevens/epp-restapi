# XML to JSON documentation

This directory gives examples of EPP requests in both XML and JSON format

## How XML is converted

At its most basic the XML is converted to JSON like this

	<xml-tag-name>some data value</xml-tag-name>

becomes

	{ "xml-tag-name": "some data value" }
