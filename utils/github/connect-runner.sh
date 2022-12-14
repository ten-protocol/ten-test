#!/bin/bash

help_and_exit() {
    echo ""
    echo "Usage: $(basename "${0}") ssh_key=<key> --resource_group=<group> --name=<name>"
    echo " "
    echo "where: "
    echo "  ssh_key             The name of the SSH private key to use"
    echo "  resource_group      The name of the resource group to use (default SystemTestHostedRunner)"
    echo "  name                The name of the VM instance (default LocalTestnetRunner) "
    echo ""
    exit 1
}

resource_group=SystemTestHostedRunner
name=LocalTestnetRunner

for argument in "$@"
do
    key=$(echo $argument | cut -f1 -d=)
    value=$(echo $argument | cut -f2 -d=)

    case "$key" in
            --ssh_key)                  ssh_key=${value} ;;
            --resource_group)           resource_group=${value} ;;
            --name)                     name=${value} ;;
            --help)                     help_and_exit ;;
            *)
    esac
done

if [[ -z ${ssh_key:-} ]];
then
    help_and_exit
fi

# get the IP
IP=`az vm show -d -g ${resource_group}  -n ${name} --query publicIps -o tsv`

# connect using given SSH key
ssh -i ${ssh_key} azureuser@$IP
