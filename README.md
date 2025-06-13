## Overview
Repo for automation configure Android, MacOS, Linux  

## Playbooks Android
Ping hosts  
`ansible-playbook -v --vault-password-file ../.vault_pass -i inventory playbooks/ping/main.yml --limit m52.pro`  

Update device  
`ansible-playbook -v --vault-password-file ../.vault_pass -i inventory playbooks/conf_new_server/main.yml --limit m52.pro --tag template`  

## Playbooks Linux
Configure backup server  
`ansible-playbook -v --vault-password-file ../.vault_pass -i inventory playbooks/conf_new_server_duman/main.yml --limit duman.pro`   

Configure main server  
`ansible-playbook -v --vault-password-file ../.vault_pass -i inventory playbooks/conf_new_server_erlan/main.yml --limit erlan.pro`  

## Playbooks Macbook
Ping hosts  
`ansible-playbook -v --vault-password-file ../.vault_pass -i inventory playbooks/ping/main.yml`  

Update device  
`ansible-playbook -v --vault-password-file ../.vault_pass -i inventory playbooks/conf/main.yml`  

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
