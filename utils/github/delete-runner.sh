#!/bin/bash

help_and_exit() {
    echo ""
    echo "Usage: $(basename "${0}") --resource_group=<group> >"
    echo " "
    echo "where: "
    echo "  resource_group      The name of the resource group to use (default SystemTestHostedRunner)"
    echo ""
    exit 1
}

resource_group=SystemTestHostedRunner

for argument in "$@"
do
    key=$(echo $argument | cut -f1 -d=)
    value=$(echo $argument | cut -f2 -d=)

    case "$key" in
            --resource_group)           resource_group=${value} ;;
            --help)                     help_and_exit ;;
            *)
    esac
done

# delete resources in the resource group
az group delete --name ${resource_group}
