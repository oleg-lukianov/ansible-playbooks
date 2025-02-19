#!/usr/bin/bash


pid=$(ps -ef | grep backup_from_sftp_to_hdd | grep -v grep | grep -v tee |  awk '{print $2}')

echo ""
echo "kill $pid"

echo ""
ps -ef | grep sleep | grep -v grep | grep -v tee

echo ""
echo ""
