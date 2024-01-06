#!/bin/bash

#  For Termux
#
#  bash /storage/emulated/0/scripts/tar.sh -create | tee -a /storage/emulated/0/scripts/backup/tar.log
#  bash /storage/emulated/0/scripts/tar.sh -delete | tee -a /storage/emulated/0/scripts/backup/tar.log
#  bash /storage/emulated/0/scripts/tar.sh -check_backup | tee -a /storage/emulated/0/scripts/backup/tar.log

version="1.01 - 27.12.2019";
version="1.02 - 30.12.2019";
version="1.03 - 10.03.2020";
version="1.04 - 02.01.2024";

path=$(dirname "$0");
path="/storage/emulated/0/scripts";

create_tar() {
    echo "Creating ($(date '+%F %T')).....";
    mkdir /storage/emulated/0/scripts/backup 2>/dev/null;
    cd /storage/emulated/0/scripts/backup || exit;
    tar --exclude="*.tar.gz" --exclude="*tar.log" --exclude="*.apk" --exclude=".git" -zcvf scripts_"$(date "+%F")".tar.gz --absolute-names $path;
    echo "END version $version !!!";
    echo "";
}

delete_tar() {
    echo "Deleting ($(date '+%F %T')).....";
    echo "path=$path";
    find $path/* -name "scripts_*.tar.gz" -mtime +30 -delete;
    echo "END version $version !!!";
    echo "";
}

check_backup() {
    file_conf="${0//sh/conf/}";
    file_alarm="${0//sh/alarm/}";
    logs=$(find /data/data/com.termux/files/home/storage/external-1/ -not -path "*.scripts/*" -type f -name "backup_android_lftp_rsync.log");
    ALL=();
    printf "Updated: " > "$file_alarm";

    for log in $logs; do
        changed="not update";
        device=$(echo "$log" | sed 's/\/data\/data\/com.termux\/files\/home\/storage\/external-1\/.backup_//g');
        device=$(echo "$device" | sed 's/\/scripts\/backup\/backup_android_lftp_rsync.log//g');
        device_cksum=$(cksum "$log" | cut -f1 -d' ');
        device_cksum_prev=$(grep "$device" "$file_conf" | sed "s/$device=//g");
        ALL+=("\n$device=$device_cksum");
        
        if [[ $device_cksum_prev -ne $device_cksum ]]; then
            changed="updated";
            printf "%s " "$device" >> "$file_alarm";
        fi;
        
        echo "$device = prev=$device_cksum_prev last=$device_cksum  $changed";
    done;
    
    echo -e "${ALL[@]}" > "$file_conf";
    echo "END version $version !!!";
}


if [[ "$1" =~ "-create" ]]; then
    create_tar;
    
elif [[ "$1" =~ "-delete" ]]; then
    delete_tar;
    
elif [[ "$1" =~ "-check_backup" ]]; then
    check_backup;
    
else
    echo "Version $version";
    echo "Not parameters (-create, -delete, -check_backup)";
fi

exit 0;
