#!/bin/bash

help_and_exit() {
    echo ""
    echo "Usage: $(basename "${0}") ssh_key=<key> --name=<name>"
    echo " "
    echo "where: "
    echo "  ssh_key             *Optional* The name of the SSH private key to use (default ~/.ssh/id_rsa)"
    echo "  name                *Optional* The name of the VM instance (default ten-test-gh-runner) "
    echo ""
    exit 1
}

ssh_key=~/.ssh/id_rsa
name=ten-test-gh-runner
group=ten-test-repo

for argument in "$@"
do
    key=$(echo $argument | cut -f1 -d=)
    value=$(echo $argument | cut -f2 -d=)

    case "$key" in
            --ssh_key)                  ssh_key=${value} ;;
            --name)                     name=${value} ;;
            --help)                     help_and_exit ;;
            *)
    esac
done

# get the IP
IP=`az vm show -d -g ${group}  -n ${name} --query publicIps -o tsv`

# connect using given SSH key
echo Connecting to tenadmin@$IP
ssh -i ${ssh_key} tenadmin@$IP
