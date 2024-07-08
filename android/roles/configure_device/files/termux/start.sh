#!/bin/bash

count_crond=$(pgrep -fc crond);
count_sshd=$(pgrep -fc sshd);

if [[ $count_crond -lt 1 ]]; then
    # crond -L /storage/emulated/0/scripts/termux/crond.log;
    busybox crond;
    count_crond=$(pgrep -fc crond);
    echo "Started.... (count_crond=$count_crond)";
else
    echo "Already running CROND.... (count_crond=$count_crond)";
fi

if [[ $count_sshd -lt 1 ]]; then
    sshd;
    count_sshd=$(pgrep -fc sshd);
    echo "Started.... (count_sshd=$count_sshd)";
else
    echo "Already running SSHd.... (count_sshd=$count_sshd)";
fi

#  tcpsvd -vE 0.0.0.0 8021 ftpd -wv /storage/emulated/0/Tasker

bash /storage/emulated/0/scripts/termux/github_update.sh 2>/dev/null 1>/dev/null &
date '+%F %T' >> /storage/emulated/0/scripts/backup/start.log
