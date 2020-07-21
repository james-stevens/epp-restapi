# epp-restapi

`epp-restapi` is a Python/Flask service to provide a rest/api for EPP domain registration / management.
It does this by providing a transparent proxy to an existing EPP registry service. 
The XML<->JSON translation is done by `xmltodict`.

It can keep multiple EPP sessions open and `nginx` will load-balance between them.

The session is only opened when the first request comes in and is held open. This can cause a small delay when getting a response
from the first request.

If the connection fails, it will attempt to reconnect before reporting an error to the caller.
As the EPP service may be unavailable at times, it will be necessary for the program calling
this API to have its own queueing & retrying system.

For a full understanding of the EPP object request format, see 
- [RFC 5730 - General](https://tools.ietf.org/html/rfc5730)
- [RFC 5731 - Domains](https://tools.ietf.org/html/rfc5731)
- [RFC 5732 - Contacts](https://tools.ietf.org/html/rfc5732)
- [RFC 5733 - Hosts](https://tools.ietf.org/html/rfc5733)


All requests should be POSTed to `/epp/api/v1.0/request`


## Difference in the object data

In EPP/XML
- all requests are wrapped with `<epp><command> ... </command></epp>`
- every transaction has a transaction-id which must be repeated back in the response.
- all response are wrapped with `<epp><response> ... </response></epp>`

In all three cases, these features are handled automatically by the rest/api code, so you
are not required to handle any of this.


## Running this on an existing server

Required software
- flask
- xmltodict
- gunicorn
- apscheduler
- nginx

I used Python `v3.8.1`, Flask `v1.1.2` & xmltodict `v0.12.0`, but to make life easier, there is a `Dockerfile` which runs it all
in a container. This is linked to the `docker.com` container `jamesstevens / epp-rest_api`, which gets automatically rebuilt
based on this `github` repo.

You can run a single thread by hand, in Flask, just by running `./epprest.py`, but this should be used for debugging only.
NOTE: You will need to set up the appropriate environments variables first (see below).


For more information in the XML to JSON translation done by `xmltodict`, see the `XML_JSON` directory.


The directory `Your-Container` is provided to give you an easy way to build your own customised container based on
the standard one.


# The Container

The container runs Python/Flask (under `gunicorn`) and `nginx` to provide a rest/api to any EPP domain registry service. The rest/api runs in `HTTPS` on port `800`.

All server processes are run under the `busybox` supervisor `/sbin/init`. There is one `gunicorn` process for each EPP Session and one `nginx` process
that round-robin load-balances the rest/api calls across the EPP Sessions.

If you run a `docker stop` on the container, `/sbin/init` will do a clean shutdown.

The container is designed to run read-only. You don't have to run it this way, but it does provide a little more security.

The scripts `dkmk` and `dkrun` will build & run the container, respectively.

## Required Environment

It requires four environment settings, for example provided using the docker option `--env-file`, these are
```
 EPP_SERVER=<server-fqdn>
 EPP_USERNAME=<username>
 EPP_PASSWORD=<password>
 EPP_SESSIONS=<num-of-epp-sessions> (optional, default=1)
 EPP_KEEPALIVE=<mins-between-keepalive> (optional, default=disabled)
```

`EPP_SERVER` - the FQDN of the EPP server to connect to. This server must have a correctly publicly verifiable certificate

`EPP_USERNAME` & `EPP_PASSWORD` - your login to the server

`EPP_SESSIONS` - the number of simultaneous EPP sessions to start - these will be load-balanced using `nginx`

`EPP_KEEPALIVE` - time in minutes between sending `<hello>` requests to the EPP Server to ensure the connection is still up.
If this is `0` or not present, then no keep-alive is done. NOTE: keep-alive shouldn't really be necessary as lost sessions will be seamlessly reconnected.


The first four are checked by the start-script, so if they are missing the container will refuse to run.


## Required Certificate

Included in the container is a certificate which has been created using a **private** certificate authority. The `PEM` for this private CA is included in the `github` repo.

By default this private certificate is used for both the `TLS` in `nginx` and as the required client certificate for the `EPP` connection. This is almost certainly **NOT** what you would want in production use, so they should probably both be replaced. It is highly likely that an external EPP server will not accept a privately signed certificate.

The `nginx` PEM lives in `/etc/nginx/certkey.pem` and the EPP client one lives in `/opt/certkey.pem` - potentially you could use the same one for both, if you wish.

## Probably Required Access Control
The REST/API is protected by user-names and passwords in the file `/etc/nginx/htpasswd`, the only default login has the user-name `username` and the password `password`. You should probably change this - using the Apache utility `htpasswd` to create a new htpasswd file.

Remember, because your EPP login is held by the container, this HTTP Authentication is what stops anybody who wants to from registering domain names using your account.

## Testing the service

Assuming you have made the container with `./dkmk`, keeping all the project's default files, except you have edited the `epprest.env` to 
log into an EPP service that you have access to, and you started the container with `./dkrun` then this should work

	curl --cacert myCA.pem -d '{"hello": null }' -H 'Content-Type: application/json' \
		https://username:password@json.jrcs.net:800/epp/api/v1.0/request | jq

the host name in the default `certkey.pem` is `json.jrcs.net`, but this should resolve to `127.0.0.1` so the
certificate should valdiate OK, if you run the `curl` on the same host that is running the container.

Otherwise, you can test using `wget` and apply the option `--no-check-certificate`

	wget -q --no-check-certificate --post-data '{"hello":null}' --header 'Content-Type: application/json' \
		-O - https://username:password@[your-host-name]:800/epp/api/v1.0/request | jq

where `[your-host-name]` is the host name or IP Address of the container.
