
# Creating a domain - no GLUE IP Address data

## XML

    <create>
      <domain:create
       xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>speed-test-1.ac</domain:name>
        <domain:period unit="y">1</domain:period>
        <domain:ns>
          <domain:hostObj>ns1.testname.com</domain:hostObj>
          <domain:hostObj>ns1.testname.ac</domain:hostObj>
        </domain:ns>
        <domain:registrant>NIC-1013</domain:registrant>
        <domain:contact type="admin">NIC-1013</domain:contact>
        <domain:contact type="tech">NIC-1013</domain:contact>
        <domain:contact type="billing">NIC-1013</domain:contact>
      </domain:create>
    </create>

## JSON
	{
	   "create": {
		  "domain:create": {
			 "@xmlns:domain": "urn:ietf:params:xml:ns:domain-1.0",
			 "domain:name": "speed-test-1.ac",
			 "domain:period": {
				"@unit": "y",
				"#text": "1"
			 },
			 "domain:ns": {
				"domain:hostObj": [
				   "ns1.testname.com",
				   "ns1.testname.ac"
				]
			 },
			 "domain:registrant": "NIC-1013",
			 "domain:contact": [
				{
				   "@type": "admin",
				   "#text": "NIC-1013"
				},
				{
				   "@type": "tech",
				   "#text": "NIC-1013"
				},
				{
				   "@type": "billing",
				   "#text": "NIC-1013"
				}
			 ]
		  }
	   }
	}
