# epp-restapi

`epp-restapi` is a Python/Flask service to provide a rest/api for EPP domain registration / management.
It does this by providing a transparent proxy to an existing EPP registry service. 
The XML<->JSON translatio is done by `xmltodict`.

It can keep multiple EPP sessions open and `nginx` will load-balance between them.

The session is only opened when the first request comes in and is held open. This can cause a small delay when getting a reponse
from the first request.

If the connection fails, it will attempt to reconnect before reporting an error to the caller.
As the EPP service may be unavailable at times, it will be necessary for the program calling
this API to have its own queueing & retrying system.


## Running this on an existing server

Requires the python modules
- flask
- xmltodict
- gunicorn
- apscheduler
- nginx

I used Python `v3.8.1`, Flask `v1.1.2` & xmltodict `v0.12.0`, but to make life easier, there is a `Dockerfile` which runs it all
in a container. This is linked to the `docker.com` container `jamesstevens / epp-rest_api`, which gets automatically rebuilt

You can run a single thread by hand, in Flask, just by running `./epprest.py`, but this should be used for debugging only.


For more information in the XML to JSON translation done by `xmltodict`, see the `XML_JSON` directory.


The directory `Your-Container` is provided to give you an easy way to build your own customised container based on
the standard one.


# The Container

The container runs Python/Flask (under `gunicorn`) and `nginx` to provide a rest/api to any EPP domain registry service. The rest/api runs in `HTTPS` on port `800`.

All server processes are run under the `busybox` supervisor `/sbin/init`. There is one `gunicorn` process for each EPP Session and one `nginx` process
that round-robin load-balances the rest/api calls accross the EPP Sessions.

If you run a `docker stop` on the container, `/sbin/init` will do a clean shutdown.


## Required Environment

It requires four environment settings, for example provided using the docker option `--env-file`, these are
```
 EPP_SERVER=<server-fqdn>
 EPP_USERNAME=<username>
 EPP_PASSWORD=<password>
 EPP_SESSIONS=<num-of-epp-sessions>
 EPP_KEEPALIVE=<mins-between-keepalive> (optional)
```

`EPP_SERVER` - the FQDN of the EPP server to connect to. This server must have a correctly publicly verifiable certificate

`EPP_USERNAME` & `EPP_PASSWORD` - your login to the server

`EPP_SESSIONS` - the number of simultaneous EPP sessions to start - these will be load-balanced using `nginx`

`EPP_KEEPALIVE` - time in minutes between sending `<hello>` requests to the EPP Server to ensure the connection is still up.
If this is `0` or not present, then no keep-alive is done. NOTE: keep-alive shouldn't really be necessary as lost sessions will be seamlessly reconnected.


## Required Certificate

Included in the container is a certificate which has been created using a **private** certificate authority. The `PEM` for this private CA is included in the `github` repo.

By default this private certificate is used for both the `TLS` in `nginx` and as the required client certificate for the `EPP` connection. This is almost certainly **NOT** what you would want in production use, so they should probably both be replaced. It is highly likely that an external EPP server will not accept a privately signed certificate.

The `nginx` PEM lives in `/etc/nginx/certkey.pem` and the EPP client one lives in `/opt/certkey.pem` - potentially you could use the same one for both, if you wish.

## Probably Required Login
The REST/API is protected by user-names and passwords in the file `/etc/nginx/htpasswd`, the only default login has the user-name `username` and the password `password`. You should probably change this - using the Apache utility `htpasswd` to create a new htpasswd file.

Remember, becuase your EPP login is held by the container, this HTTP Authentication is what stops anybody who wants to from registering domain names using your account.

## Misc
In the `github` project, the scripts `dkmk` and `dkrun` will remake & run the container.

For more general dev info, see `github`.
