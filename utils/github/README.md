## Steps to set up the runner
Below lists the steps to setup a remotely managed github runner on an Ubuntu 20.04 VM. 

# Create and connect
Run the utility scripts to create the VM and connect;

```bash
# create the VM
 ./utils/github/create-runner.sh --name=SystemTestRunner1 
 
# connect to the VM
./utils/github/connect-runner.sh --name=SystemTestRunner1 
```

# Install dependencies
Once connected to the VM run `sudo ./install.sh` script to install all the required dependencies for running the tests. 
Once done ensure the correct version of solc is used, and set permissions for docker using the below;

```bash
# install and use 0.8.18
solc-select install 0.8.18
solc-select use 0.8.18

# put this in the .bashrc file to doubly ensure it is picked up by the runner
export SOLC_VERSION=0.8.18

# set permissions for docker
sudo groupadd docker
sudo usermod -aG docker obscuro
newgrp docker
```

# Configure the runner
Go to the [runners](https://github.com/obscuronet/obscuro-test/settings/actions/runners) section of the `obscuro-test`
repo and click on new runner. Follow the commands there to install and run the new runner. 