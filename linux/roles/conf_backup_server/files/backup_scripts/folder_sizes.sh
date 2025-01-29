#!/usr/bin/bash

ARRAY=($(cat /var/ftp/pub/RAID1_500GB/TEMP/folder_sizes.txt | tr '\t' ';' | tr '$' '\n'));

#IFS=$'$';
for x in "${ARRAY[@]}"; do
#   echo "x = $x";
    TEMP=(${x//;/ })
    echo "size = ${TEMP[0]} --- folder = ${TEMP[1]}"
    zabbix_sender -z erlan.pro -s "duman.pro" -k "folder_sizes_[${TEMP[1]}]" -o "${TEMP[0]}";

done;
#unset IFS


exit 0;