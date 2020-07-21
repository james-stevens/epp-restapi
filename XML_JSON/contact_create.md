# Creating a contact record

## XML
    <create>
      <contact:create xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>sh8013</contact:id>
        <contact:postalInfo type="int">
          <contact:name>John O'Doe</contact:name>
          <contact:org>Example Inc.</contact:org>
          <contact:addr>
            <contact:street>123 Example Dr.</contact:street>
            <contact:street>Suite 100</contact:street>
            <contact:street>My Desk</contact:street>
            <contact:city>Some City</contact:city>
            <contact:sp>VA</contact:sp>
            <contact:pc>20166-6503</contact:pc>
            <contact:cc>US</contact:cc>
          </contact:addr>
        </contact:postalInfo>
        <contact:voice x="1234">+1.7035555555</contact:voice>
        <contact:fax>+1.7035555556</contact:fax>
        <contact:email>jdoe@example.com</contact:email>
        <contact:disclose flag="0">
          <contact:voice/>
          <contact:addr/>
          <contact:email/>
        </contact:disclose>
      </contact:create>
    </create>

## JSON

     "create": {
        "contact:create": {
           "@xmlns:contact": "urn:ietf:params:xml:ns:contact-1.0",
           "contact:id": "sh8013",
           "contact:postalInfo": {
              "@type": "int",
              "contact:name": "John O'Doe",
              "contact:org": "Example Inc.",
              "contact:addr": {
                 "contact:street": [
                    "123 Example Dr.",
                    "Suite 100",
                    "My Desk"
                 ],
                 "contact:city": "Some City",
                 "contact:sp": "VA",
                 "contact:pc": "20166-6503",
                 "contact:cc": "US"
              }
           },
           "contact:voice": {
              "@x": "1234",
              "#text": "+1.7035555555"
           },
           "contact:fax": "+1.7035555556",
           "contact:email": "jdoe@example.com",
           "contact:disclose": {
              "@flag": "0",
              "contact:voice": null,
              "contact:addr": null,
              "contact:email": null
           }
        }
     },
     "clTRID": "ABC-12345"
  }
}
}
