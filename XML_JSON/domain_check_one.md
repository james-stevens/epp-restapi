# Check if a domain is available

## XML

  
    <check>
      <domain:check xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>example.com</domain:name>
      </domain:check>
    </check>


## JSON

     "check": {
        "domain:check": {
           "@xmlns:domain": "urn:ietf:params:xml:ns:domain-1.0",
           "domain:name": "example.com"
        }
     }
