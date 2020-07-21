# Create a domain with GLUE Records

    <create>
      <domain:create xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>exmaple.com</domain:name>
        <domain:period unit="y">1</domain:period>

          <domain:ns>
             <domain:hostAttr>
               <domain:hostName>ns1.example.com</domain:hostName>
               <domain:hostAddr ip="v4">192.0.1.1</domain:hostAddr>
               <domain:hostAddr ip="v6">1080:0:0:0:8:800:200C:417A</domain:hostAddr>
             </domain:hostAttr>

             <domain:hostAttr>
               <domain:hostName>NS1.exmaple.com</domain:hostName>
               <domain:hostAddr ip="v4">192.0.2.1</domain:hostAddr>
               <domain:hostAddr ip="v6">2080:0:0:0:8:800:200C:417A</domain:hostAddr>
             </domain:hostAttr>

             <domain:hostAttr>
               <domain:hostName>ns2.exmaple.com</domain:hostName>
               <domain:hostAddr ip="v4">192.0.9.9</domain:hostAddr>
             </domain:hostAttr>

             <domain:hostAttr>
               <domain:hostName>ns3.example.com</domain:hostName>
             </domain:hostAttr>

           </domain:ns>

        <domain:registrant>sh8013</domain:registrant>
        <domain:contact type="admin">sh8013</domain:contact>
        <domain:contact type="tech">sh8013</domain:contact>
        <domain:contact type="billing">sh8013</domain:contact>
      </domain:create>
    </create>

# JSON

     "create": {
        "domain:create": {
           "@xmlns:domain": "urn:ietf:params:xml:ns:domain-1.0",
           "domain:name": "exmaple.com",
           "domain:period": {
              "@unit": "y",
              "#text": "1"
           },
           "domain:ns": {
              "domain:hostAttr": [
                 {
                    "domain:hostName": "ns1.example.com",
                    "domain:hostAddr": [
                       {
                          "@ip": "v4",
                          "#text": "192.0.1.1"
                       },
                       {
                          "@ip": "v6",
                          "#text": "1080:0:0:0:8:800:200C:417A"
                       }
                    ]
                 },
                 {
                    "domain:hostName": "NS1.exmaple.com",
                    "domain:hostAddr": [
                       {
                          "@ip": "v4",
                          "#text": "192.0.2.1"
                       },
                       {
                          "@ip": "v6",
                          "#text": "2080:0:0:0:8:800:200C:417A"
                       },
                    ]
                 },
                 {
                    "domain:hostName": "ns2.exmaple.com",
                    "domain:hostAddr": {
                       "@ip": "v4",
                       "#text": "192.0.9.9"
                    }
                 },
                 {
                    "domain:hostName": "ns3.example.com"
                 }
              ]
           },
           "domain:registrant": "sh8013",
           "domain:contact": [
              {
                 "@type": "admin",
                 "#text": "sh8013"
              },
              {
                 "@type": "tech",
                 "#text": "sh8013"
              },
              {
                 "@type": "billing",
                 "#text": "sh8013"
              }
           ]
        }
     }
