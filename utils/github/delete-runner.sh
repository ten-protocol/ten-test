#!/bin/bash

help_and_exit() {
    echo ""
    echo "Usage: $(basename "${0}") --name=<name>"
    echo " "
    echo "where: "
    echo "  name                *Optional* The name of the VM instance (default SystemTestRunner) "
    echo ""
    exit 1
}

ssh_key=~/.ssh/id_rsa
name=SystemTestRunner

for argument in "$@"
do
    key=$(echo $argument | cut -f1 -d=)
    value=$(echo $argument | cut -f2 -d=)

    case "$key" in
            --name)                     name=${value} ;;
            --help)                     help_and_exit ;;
            *)
    esac
done

# delete the vm in the resources group
az vm delete --resource-group SystemTestRunners --name ${name}