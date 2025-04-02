#!/bin/bash

set -x

cat /proc/sys/crypto/fips_enabled

openssl version

openssl list -providers

echo 1 > /tmp/file
openssl md5 /tmp/file
