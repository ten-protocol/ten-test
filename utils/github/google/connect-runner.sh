#!/bin/bash

help_and_exit() {
    echo ""
    echo "Usage: $(basename "${0}") ssh_key=<key> --name=<name>"
    echo " "
    echo "where: "
    echo "  ssh_key             *Optional* The name of the SSH private key to use (default ~/.ssh/id_rsa)"
    echo "  name                *Optional* The name of the VM instance (default ten-test-alibaba-runner-01) "
    echo ""
    exit 1
}

ssh_key=~/.ssh/id_rsa
name=ten-test-alibaba-runner-01
region=eu-west-1

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
echo Instance in region $region
aliyun ecs DescribeInstances --RegionId "${region}" --output cols=InstanceName,PublicIpAddress rows=Instances.Instance[]

IP=`aliyun ecs DescribeInstances --RegionId "${region}" --output cols=InstanceName,PublicIpAddress rows=Instances.Instance[] | grep ${name} | awk -F'[][]' '{print $3}'`

# connect using given SSH key
echo Connecting to root@$IP
ssh -i ${ssh_key} root@$IP
