# domain_check - batch

## XML


    <check>
      <domain:check xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>example1.com</domain:name>
        <domain:name>example2.com</domain:name>
        <domain:name>example3.com</domain:name>
        <domain:name>example4.com</domain:name>
        <domain:name>example5.com</domain:name>
        <domain:name>example6.com</domain:name>
        <domain:name>example7.com</domain:name>
        <domain:name>example8.com</domain:name>
        <domain:name>example9.com</domain:name>
      </domain:check>
    </check>


## JSON

     "check": {
        "domain:check": {
           "@xmlns:domain": "urn:ietf:params:xml:ns:domain-1.0",
           "domain:name": [
              "example1.com",
              "example2.com",
              "example3.com",
              "example4.com",
              "example5.com",
              "example6.com",
              "example7.com",
              "example8.com",
              "example9.com"
           ]
        }
     }
