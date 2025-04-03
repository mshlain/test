#!/bin/bash

echo "========================="
echo "  Testing fips in kernel"
echo "========================="
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
echo "========================="
echo " Print openssl location  "
echo "========================="
echo ""
command_text="which openssl"
echo "Command: $command_text"
result=$(eval "$command_text")
echo "Result:  $result"

echo ""
echo ""
echo "========================="
echo " Print openssl version  "
echo "========================="
echo ""
command_text="openssl version -a"
echo "Command: $command_text"
result=$(eval "$command_text")
echo "Result:  $result"

echo ""
echo ""
echo "========================="
echo " Print openssl providers "
echo "========================="
echo ""
command_text="openssl list -providers"
echo "Command: $command_text"
result=$(eval "$command_text")
echo "Result:  $result"

# openssl list -providers

# echo 1 > /tmp/file
# openssl md5 /tmp/file