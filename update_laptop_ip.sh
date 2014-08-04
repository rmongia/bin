#!/bin/bash

set -e

LAPTOP_IP=`echo $SSH_CLIENT | cut -d' ' -f1`
TINYDNS_DATA='/etc/tinydns/root/data'
TINYDNS_ADD_HOST='./add-host'
TINYDNS_MAKE='make'
TINYDNS_TEMP='/tmp/tinydns-data.tmp'
TINYDNS_ROOT='/etc/tinydns/root'
LAPTOP_NAME='rmongia-laptop.internal'
LAPTOP_DOMAIN='internal'

grep -v $LAPTOP_NAME $TINYDNS_DATA > $TINYDNS_TEMP

pushd $TINYDNS_ROOT
sudo mv $TINYDNS_TEMP $TINYDNS_DATA
sudo $TINYDNS_ADD_HOST $LAPTOP_NAME $LAPTOP_IP
sudo $TINYDNS_MAKE 
popd
