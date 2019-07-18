
#!/bin/bash
branch=$1
js_container_name=$2

if [[ "$OSTYPE" == "linux-gnu" ]]; then
        OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="mac"

echo " [*] Add sshkey"
eval `ssh-agent -s`
ssh-keygen
ssh-add 
sshkey=$(ssh-add -L)

echo " [*] Install requirements"
if [[ OS == "linux" ]]; then
        apt-get install -r linux_requirements
elif [[ OS == "mac" ]]; then
        apt-get install -r mac_requirements
         
echo " [*] Running instaltion tests .."
nosetests-3.4 -v -s test_instaltion.py --tc-file=config.ini  --tc=main.os_type:os --tc=main.ssh_key:sshkey --tc=main.branch=branch --tc=main.container_name=js_container_name

