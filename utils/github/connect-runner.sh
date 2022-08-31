#!/bin/bash

if [ $# -ne 1 ]; then
  echo "You must specify an SSH key to use in the connection"
  exit
fi
KEY=$1

# get the IP
IP=`az vm show -d -g SystemTestHostedRunner  -n LocalTestnetRunner --query publicIps -o tsv`

# connect using given SSH key
ssh -i $KEY azureuser@$IP
