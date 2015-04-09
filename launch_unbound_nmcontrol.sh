#!/bin/bash

# Note: right now you must run this as root.  Yes, this sucks.
# Don't use it in a production environment until that is fixed.

# to set this up on Fedora, as root:
# echo "dns=dnsmasq">>/etc/NetworkManager/NetworkManager.conf
# echo "server=/bit/127.0.0.2">/etc/NetworkManager/dnsmasq.d/bit-tld

unbound -c ./unbound_nmcontrol.conf
