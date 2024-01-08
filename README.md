## Overview
Repo for automation configure Android, MacOS, Linux  

## Playbooks Android
Ping hosts  
`ansible-playbook --vault-password-file .vault_pass -i inventory playbooks/ping/main.yml --limit m52_pro`  

Update device  
`ansible-playbook --vault-password-file .vault_pass -i inventory playbooks/configure_device/main.yml --limit m52_pro`  

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
`ansible-playbook --vault-password-file .vault_pass -i inventory playbooks/configure_device/main.yml --limit m52 --start-at-task="Create a symbolic link for 'a71.pro'"`

Encrypt/decrypt inventory  
`ansible-vault view --vault-password-file .vault_pass inventory`  
`ansible-vault edit --vault-password-file .vault_pass inventory`  
`ansible-vault decrypt --vault-password-file .vault_pass inventory`  
`ansible-vault encrypt --vault-password-file .vault_pass inventory`  
