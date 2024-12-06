#!/bin/bash
#  termux-setup-storage
#  bash /storage/emulated/0/scripts/termux/run_for_new_phone.sh -install
#  bash /storage/emulated/0/scripts/termux/run_for_new_phone.sh -restore
#  sshd
#  ansible-playbook --vault-password-file ../.vault_pass -i inventory playbooks/configure_device/main.yml --limit a71_pro

#  bash /storage/emulated/0/scripts/termux/run_for_new_phone.sh -copy
#  bash /storage/emulated/0/scripts/termux/run_for_new_phone.sh -restore

#  HELP  #
#  Repolist
#  cat  /data/data/com.termux/files/usr/etc/apt/sources.list

version="1.01 - 04.07.2024";

restore_ssh_home_dir="/storage/emulated/0/scripts/termux/.ssh/"
restore_ssh_etc_dir="/storage/emulated/0/scripts/termux/ssh"
ssh_etc_dir="/data/data/com.termux/files/usr/etc/ssh"

copy_config() {
    echo "Config copying...."

    if [ ! -d $restore_ssh_home_dir ]; then
        echo "Create dir $restore_ssh_home_dir"
        mkdir $restore_ssh_home_dir
    else
        echo "Dir is exist $restore_ssh_home_dir"
    fi

    if [ ! -d $restore_ssh_etc_dir ]; then
        echo "Create dir $restore_ssh_etc_dir"
        mkdir $restore_ssh_etc_dir
    else
        echo "Dir is exist $restore_ssh_etc_dir"
    fi

    echo "Copy keys from ~/.ssh/ to $restore_ssh_home_dir"
    cp -v -f -r ~/.ssh/* "$restore_ssh_home_dir"

    echo "Copy keys from $ssh_etc_dir/ to $restore_ssh_etc_dir/"
    cp -v -f -r $ssh_etc_dir/ssh_host_* $restore_ssh_etc_dir/

    echo ""
}

restore_config() {
    echo "Config restoring...."
    if [ ! -d ~/.ssh ]; then
        echo "Create dir ~/.ssh"
        mkdir ~/.ssh
    else
        echo "Dir is exist ~/.ssh"
    fi

    echo "Restore keys from $restore_ssh_home_dir to ~/.ssh/"
    cp -v -f -r "$restore_ssh_home_dir" ~/

    echo "Restore keys from $restore_ssh_etc_dir to $ssh_etc_dir/"
    cp -v -f -r "$restore_ssh_etc_dir/" "$ssh_etc_dir/"

    echo ""
}

install_packages() {
    echo "Packages installing...."
    pkg install openssh python -y

    echo ""
}


if [[ "$1" =~ "-copy" ]]; then
    copy_config;

elif [[ "$1" =~ "-restore" ]]; then
    restore_config;

elif [[ "$1" =~ "-install" ]]; then
    install_packages;

else
    echo "Version $version";
    echo "Not parameters (-copy, -restore -install)";
fi

