Erroneous
=========
Erroneous allows you to mark all packages of a [Spacewalk](http://spacewalk.redhat.com) channel as errata. It allows you to distinguish between security and bugfix erratas.


How it works:
-------------
1.  Erroneous connects to the spacewalk server through the xmlrpc api and asks the server for a list of all packages in the specified channel(s).

2.  A unique errata name is generated for each packages in the pattern:
    package:name-package:version.pacakge:release_errataGen
    i.e.: kernel-firmware-2.6.32.131.17.1.el6_errataGen
    The architecture is not included in the errata name. This results in one errata for all archs containing packages for all archs.

3.  Erroneous then searches for an existing errata with that name and appends the package to the errata, if it exists, or creates a new errata if no errata is found.


Setup
-----
The config file (erroneous.conf) consists of a [main] part and channels.

### The [main] section
The [main] section has 4 key elements:

1.  The server URL

    The `url` key defines the server URL. I.e.: https://yourspacewalkserver/rpc/api

2.  The username

    The `user` key specifies a valid username, which should have the privileges to edit all software channels specified in the config.

3.  The password

    `pass` specifies the password for `user`.

4.  Debug Mode

    default: false
    
    possibilities: true | false

    If `debug` is set to true the script gets verbose.

### The Channels
A Channel consists of a chanel label ([chanelLabel]), severity and which product it belongs to.

1.  The channel label

    A new channel is introduced by creating a new section and naming it as the chanels name you want to create errata for.

2.  The severity

    possibilities: security | bugfix

    The `severity` specifies, if the packages in the channel should be decorated with a security or a bugfix(fature) errata.

3.  The product

    Here you can provide the `product`.

FAQ:
----
How do I select/delete all auto generated errata?

search for the string "errataGen"
