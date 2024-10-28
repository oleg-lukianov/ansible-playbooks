## Overview
Repo for automation configure Android, MacOS, Linux  

## Playbooks Android
Ping hosts  
`ansible-playbook --vault-password-file ../.vault_pass -i inventory playbooks/ping/main.yml --limit m52_pro`  

Update device  
`ansible-playbook --vault-password-file ../.vault_pass -i inventory playbooks/configure_device/main.yml --limit m52_pro --tag template`  

## Playbooks Linux
Ping hosts  
`ansible-playbook --vault-password-file ../.vault_pass -i inventory playbooks/ping/main.yml --limit duman_pro`  

Configure backup server  
`ansible-playbook --vault-password-file ../.vault_pass -i inventory playbooks/configure_backup_server/main.yml --limit duman_pro`  

## ansible-lint
Update ansible-lint from PIP  
`pip freeze | grep ansible-lint`  
`pip install ansible-lint --upgrade`  

Install from BREW  
`arch -arm64 brew install ansible-lint python-markupsafe`  

Check code  
`ansible-lint playbooks/*`  
`ansible-lint roles/*`  

## Help commands
Run from specific task  
`ansible-playbook --vault-password-file ../.vault_pass -i inventory playbooks/configure_device/main.yml --limit m52_pro --start-at-task="Create a symbolic link for 'a71.pro'"`

Encrypt/decrypt inventory  
`cd android`  
`ansible-vault view --vault-password-file ../.vault_pass inventory`  
`ansible-vault edit --vault-password-file ../.vault_pass inventory`  
`ansible-vault decrypt --vault-password-file ../.vault_pass inventory`  
`ansible-vault encrypt --vault-password-file ../.vault_pass inventory`  

`ansible-vault decrypt --vault-password-file ../.vault_pass roles/configure_backup_server/files/backup_scripts/backup_from_sftp_to_hdd.sh`  
`ansible-vault encrypt --vault-password-file ../.vault_pass roles/configure_backup_server/files/backup_scripts/backup_from_sftp_to_hdd.sh`  

Create new password  
`cat /dev/urandom | tr -dc 'A-Za-z0-9!=' | head -c 32`  
Create encrypt password  
`echo 123 | base64`  
pass=MTIzCg==  
