# GEt domain information

## XML

  
    <info>
      <domain:info xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name hosts="all">exmaple.com</domain:name>
      </domain:info>
    </info>

## JSON

     "info": {
        "domain:info": {
           "@xmlns:domain": "urn:ietf:params:xml:ns:domain-1.0",
           "domain:name": {
              "@hosts": "all",
              "#text": "exmaple.com"
           }
        }
     }
