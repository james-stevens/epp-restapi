# Your container build

This directory is provided to try and give you an easy way for you to build your own custom container.

First you must copy your publicly verifiable cert/key PEM file into this directory as the file `certkey.pem`

Then run `./dkmk` - this will prompt you to create a username & password for your `rest/api` service, 
before creating your container as `my_epprest`

If you run this script more than once, you can just press `[return]` at the user-name prompt to retain the
`htpasswd` file you created the previous time.
