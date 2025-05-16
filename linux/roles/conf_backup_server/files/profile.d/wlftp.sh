#!/usr/bin/bash


pid=$(ps -ef | grep 'backup_from_sftp_to_hdd\|sleep' | grep -v grep | grep -v tee |  awk '{print $2}' | xargs)

echo ""
echo "killlftp"
echo "or"
echo "kill $pid"

echo ""
ps -ef | grep 'backup_from_sftp_to_hdd\|sleep' | grep -v grep

echo ""
echo ""
