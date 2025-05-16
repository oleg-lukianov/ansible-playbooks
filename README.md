## Overview
Repo for automation configure Android, MacOS, Linux  

## Playbooks Android
Ping hosts  
`ansible-playbook --vault-password-file ../.vault_pass -i inventory playbooks/ping/main.yml --limit m52.pro`  

Update device  
`ansible-playbook --vault-password-file ../.vault_pass -i inventory playbooks/conf_new_server/main.yml --limit m52.pro --tag template`  

## Playbooks Linux
Ping hosts  
`ansible-playbook --vault-password-file ../.vault_pass -i inventory playbooks/ping/main.yml --limit duman.pro`  

Update device  
`ansible-playbook --vault-password-file ../.vault_pass -i inventory playbooks/conf_new_server/main.yml --limit duman.pro`  

Configure backup server  
`ansible-playbook --vault-password-file ../.vault_pass -i inventory playbooks/conf_backup_server/main.yml --limit duman.pro`  

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
`ansible-playbook --vault-password-file ../.vault_pass -i inventory playbooks/conf_new_server/main.yml --limit m52.pro --start-at-task="Create a symbolic link for 'a71.pro'"`

Encrypt/decrypt inventory  
`cd android`  
`ansible-vault view --vault-password-file ../.vault_pass inventory`  
`ansible-vault edit --vault-password-file ../.vault_pass inventory`  
`ansible-vault decrypt --vault-password-file ../.vault_pass inventory`  
`ansible-vault encrypt --vault-password-file ../.vault_pass inventory`  

Create new password  
`cat /dev/urandom | tr -dc 'A-Za-z0-9!=' | head -c 32`  
Create encrypt password  
`echo 123 | base64`  
pass=MTIzCg==  
