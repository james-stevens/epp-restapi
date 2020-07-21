# Polling for server side messages

## XML - polling for messages

    <poll op="req"/>

## JSON

    { "poll": { "@op": "req" } }


## XML - acknowledging a message

    <poll op="ack" id="9"/>

## JSON

    { "poll": { "@op": "ack", "@id": "9" } }

