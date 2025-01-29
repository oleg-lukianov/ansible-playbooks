#!/usr/bin/bash

path_out="/var/ftp/pub/RAID1_500GB/DCIM";

if [[ "$path_out" == "" ]] || [[ ! -d "$path_out" ]]; then
    echo -e "\e[0;93mNo path BACKUP_DIR !!!\e[0m"
    exit 1;
fi

cd "$path_out" || exit;
find . -maxdepth 0 -type d -exec tar -uvf "/var/ftp/pub/RAID1_500GB/DCIM_Backup/{}.tar" "{}" \;

exit 0;