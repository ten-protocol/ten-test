## Steps to set up the runner
Below lists the steps to setup a remotely managed github runner on an Ubuntu 20.04 VM. The steps are not fully automated. 
A utility script exists to install all major dependencies on the VM, and to easily connect to it without having to have 
knowledge of the public IP address. Once the VM is created, Docker and the GitHub runner software should then be post 
installed for it to be ready to run tests. 

# Create and connect
Run the utility scripts to create the VM and connect;

```bash
# create the VM
 ./utils/github/create-runner.sh --ssh_key=~/.ssh/id_rsa.pub --resource_group=SystemTestHostedRunner \
                                 --name=LocalTestnetRunner --size=Standard_DC4s_v2
 
# connect to the VM
./utils/github/connect-runner.sh --ssh_key=~/.ssh/id_rsa --resource_group=SystemTestHostedRunner \
                                 --name=LocalTestnetRunner
```

# Set permissions on Docker
To set permissions for docker on the VM use the below;

```bash
sudo groupadd docker
sudo usermod -aG docker azureuser
newgrp docker
```

# Configure the runner
Go to the [runners](https://github.com/obscuronet/obscuro-test/settings/actions/runners) section of the `obscuro-test`
repo and click on new runner. The commands given should replicate those as shown below, though the TOKEN will be given 
in the portal output. Copy and paste to run on the VM. Was running you should see the runner in the list of available 
runners as being up but idle. 

```bash
# download and install (make sure it is for linux!)
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.299.1.tar.gz -L https://github.com/actions/runner/releases/download/v2.299.1/actions-runner-linux-x64-2.299.1.tar.gz
tar xzf ./actions-runner-linux-x64-2.299.1.tar.gz
./config.sh --url https://github.com/obscuronet/obscuro-test --token <TOKEN>

# start a tmux session to start the runner
export NODE_PATH=/usr/lib/node_modules/
tmux new -s github-runner
./run.sh

# exit the tmux session 
ctrl-b-d (to exit tmux)
```
