#!/bin/bash

echo "=================================================="
echo "  Test fips in kernel"
echo "=================================================="
echo ""
command_text="cat /proc/sys/crypto/fips_enabled"  # define command_text variable
echo "Command: $command_text"
echo "Expected: 1"
result=$(eval "$command_text")
echo "Result:  $result"
expected=1
if [ "$result" -eq "$expected" ]; then
    echo -e "\e[32msuccess\e[0m"
else
    echo -e "\e[31mERROR expected $expected got $result\e[0m"
fi

echo ""
echo ""
echo "=================================================="
echo " Print openssl location  "
echo "=================================================="
echo ""
command_text="which openssl"
echo "Command: $command_text"
result=$(eval "$command_text")
echo "Result:  $result"

echo ""
echo ""
echo "=================================================="
echo " Print openssl version  "
echo "=================================================="
echo ""
command_text="openssl version -a"
echo "Command: $command_text"
result=$(eval "$command_text")
echo "Result:"
echo " "
echo "$result"

echo ""
echo ""
echo "=================================================="
echo " Print openssl directory  "
echo "=================================================="
echo ""
command_text="ls -lah /usr/lib/ssl"
echo "Command: $command_text"
result=$(eval "$command_text")
echo "Result:"
echo " "
echo "$result"

echo ""
echo ""
echo "=================================================="
echo " Print openssl providers directory  "
echo "=================================================="
echo ""
command_text="ls -lah /usr/lib/ssl/providers"
echo "Command: $command_text"
result=$(eval "$command_text")
echo "Result:"
echo " "
echo "$result"

echo ""
echo ""
echo "=================================================="
echo " Print fipsmodule.cnf file  "
echo "=================================================="
echo ""
command_text="cat /usr/lib/ssl/providers/fipsmodule.cnf"
echo "Command: $command_text"
result=$(eval "$command_text")
echo "Result:"
echo " "
echo "$result"

echo ""
echo ""
echo "=================================================="
echo " Test openssl providers "
echo "=================================================="
echo ""
command_text="openssl list -providers"
echo "Command: $command_text"
result=$(eval "$command_text")
echo "Result:  $result"
if echo "$result" | grep -q "fips" && echo "$result" | grep -q "OpenSSL FIPS Provider" && echo "$result" | grep -q "status: active"; then
    echo -e "\e[32mFIPS provider is enabled successfully\e[0m"
else
    echo -e "\e[31mERROR: FIPS provider is not enabled properly\e[0m"
fi

echo ""
echo ""
echo "=================================================="
echo " Test openssl ciphers   "
echo "=================================================="
echo ""
command_text="openssl ciphers -v"
echo "Command: $command_text"
result=$(eval "$command_text")
echo "Result:  $result"

if echo "$result" | grep -q "SSLv3"; then
    echo -e "\e[31mERROR: SSLv3 is not FIPS compliant\e[0m"
else
    
    echo -e "\e[32mNo SSLv3 ciphers found, FIPS compliance is maintained\e[0m"
fi
