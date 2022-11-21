<h1 align="center">
  <img alt="obscuro logo" src=".assets/logo_fade.gif#gh-light-mode-only" width="720px"/>
  <img alt="obscuro logo" src=".assets/logo_fade_dark.gif#gh-dark-mode-only" width="720px"/>
  Obscuro Test Framework 
</h1>

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
![Python](https://img.shields.io/badge/python-3.9-blue.svg)
[![Run local tests](https://github.com/obscuronet/obscuro-test/actions/workflows/local_tests.yml/badge.svg)](https://github.com/obscuronet/obscuro-test/actions/workflows/local_tests.yml)
[![Run testnet tests](https://github.com/obscuronet/obscuro-test/actions/workflows/testnet_tests.yml/badge.svg)](https://github.com/obscuronet/obscuro-test/actions/workflows/testnet_tests.yml)

Project repo for running end to end system tests against a variety of networks, with [obscuro](https://obscu.ro/) being 
the primary network under test. Other networks supported include [ganache](https://trufflesuite.com/ganache/), 
[goerli via infura](https://infura.io/), and [geth](https://geth.ethereum.org/docs/getting-started). The repo uses the 
[pysys](https://pysys-test.github.io/pysys-test/) test framework to manage all tests and their execution. All tests are 
fully system level using [web3.py](https://web3py.readthedocs.io/en/stable/) to interact with the networks which are 
managed outside the scope of the tests (with the exception of ganache which can be started locally). Note the project is 
currently under active development and further information on running the tests will be added to this readme over time. 

Repository Structure
--------------------
The top level structure of the project is as below;

```
├── README.md            # Readme 
├── .github              # Github configuration including workflows
├── .default.properties  # Default properties file detailing connection and keys required for running 
├── pysysproject.xml     # The pysys project file detailing configuration options
├── get_artifacts.sh     # Build script to build artifacts from go-obscuro required for running Obscuro tests
├── admin                # Used for administering Obscuro testnet 
├── artifacts            # Directory to store artifacts for running Obscuro tests
├── src                  # The source root for all test code
│    ├── javascript      # A library of javascript client tooling
│    ├── python          # The python source root for pysys extensions
│    └── solidity        # A library of smart contracts 
├── tests                # The test root for all tests 
│    ├── generic         # Network agnostic tests 
│    └── obscuro         # Obscuro specific tests 
└── utils                # The project utils root for utilities used by the tests
     ├── docker          # Docker configuration and build files
     └── github          # Azure VM github self hosted running build files
```

The [.default.properties](./.default.properties) file contains properties for running the tests that are common to any 
user. User specific properties should be added into a `.username.properties` file (where `username` is the output of 
running `whoami`) at the root of the project. As this file could contain sensitive data such as account private keys, 
it should never be committed back into the main repo (the [.gitignore](./.gitignore) should prevent this). Properties 
will first be looked for in a `.username.properties` should it exist, and if not will fall back to the default properties. 


Quickstart Setup and Run (via docker)
-------------------------------------
The easiest way to set up a host to run the tests is to create a docker container with all dependencies pre-installed. 
The obscuro-test repository should be cloned into the same parent directory as 
[go-obscuro](https://github.com/obscuronet/go-obscuro) as running the tests will use the wallet_extension built from the 
working copy of go-obscuro. To build the wallet_extension and the docker container, in the root of working directory of
obscuro-test run;

```bash
./utils/docker/build_image.sh
```

Once built, to connect to the container run;

```bash
./utils/docker/run_image.sh
```


Setup and Run locally on host machine
-------------------------------------
If you want full control to develop tests, and/or to run against the go-obscuro simulation or a locally deployed 
testnet, the preferred way is to install all dependencies on the local machine. To install use the following;

### Mac OSX (Monterey 12.4)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew update
brew upgrade
brew install node
brew tap ethereum/ethereum
brew install solidity
brew install python3

npm install solc@0.8.15 --global
npm install console-stamp --global
npm install ganache --global
npm install web3 --global
npm install ethers --global
npm install commander --global

pip3 install web3
pip3 install pysys==1.6.1
pip3 install py-solc-x
```

### Linux (Ubuntu 20.04)
```bash
apt update
DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
apt-get install -y software-properties-common
add-apt-repository ppa:ethereum/ethereum
apt update
apt install -y curl
apt install -y solc

curl -sL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs
npm install console-stamp --global
npm install ganache --global
npm install web3 --global
npm install ethers --global
npm install commander --global

apt install -y python3-pip
python3 -m pip install web3
python3 -m pip install pysys==1.6.1
python3 -m pip install py-solc-x
```

Once installed it should be possible to run all tests from the pysys.py cli as described in the following sections. Note
that depending on differences in your installation and should you want to add in your own accounts on Goerli, you 
may need to override the `.default.properties` file by creating a user specific properties file e.g. 
`.username.properties` file, where `username` is the output of running `whoami`. Common overrides will inlude the path 
to various binaries used when running the tests, and account details e.g. for real accounts on Goerli. An example of an 
override properties file is as given below where binary locations and the Infura project ID for the user are set as 
overrides;

```
[binaries.darwin]
solc = /opt/homebrew/bin/solc 
ganache = /opt/homebrew/bin/ganache-cli
node = /opt/homebrew/bin/node
node_path = /opt/homebrew/lib/node_modules

[env.goerli]
ProjectID=266273d6b9a544f3ad56c725f38dfd56
```


Pre-setup required for Obscuro
------------------------------
Whilst the repo is set up to run against a variety of different networks, to run against Obscuro some specific setup 
tasks are required. This is because currently we need to allocate native OBX for gas usage to all test user accounts, and 
also for Obscuro specific tests which require tokens to be available in well known ERC20 contracts. To allocate these
you must first change directory into the `obscuro-test\admin` directory and run the below;

```bash
# to allocate on Obscuro testnet
pysys.py run fund_layer_* fund_test_users

# to allocate on Obscuro dev-testnet
pysys.py run -m obscuro.dev fund_layer_* fund_test_users

# to allocate on Obscuro local testnet
pysys.py run -m obscuro.local fund_layer_* fund_test_users

# to allocate on Obscuro simulation
pysys.py run -m obscuro.sim fund_layer_* fund_test_users
```

See the [admin README.md](admin/README.md) for more details. Note that this only needs to be performed once on startup 
of the network. 


Print and run tests
--------------------
Each test is a separate directory within `obscuro-test/tests` where the directory name denotes the testcase id. Each 
test will contain a `run.py` file (the execution and validation steps) and a `pysystest.xml` file (metadata about the 
test such as its title, purpose, supported modes it can be run in etc). To print out information on the tests, or to run 
them, change directory to `obscuro-test/tests`and run;

```bash
# print out test titles
pysys.py print 

# print out full test details
pysys.py print -f

# run the tests against Obscuro testnet
pysys.py run 

# run the tests against Obscuro dev-testnet
pysys.py run -m obscuro.dev 

# run the tests against Obscuro local testnet
pysys.py run -m obscuro.local

# run the tests against Obscuro simulation
pysys.py run -m obscuro.sim

# run the tests against a local ganache network 
pysys.py run -m ganache
```

To run the same tests against Goerli, a `.username.properties` file should be created in the root of the working 
directory of the project detailing the existing accounts pre-setup; 

```
[env.all]
Account1PK=<private key of account 1 available e.g. via metamask>
Account2PK=<private key of account 2>
Account3PK=<private key of account 3>
Account4PK=<private key of account 4>

[env.goerli]
ProjectID=<project ID>
```

To run the tests against Goerli use;

```bash
# run the tests against goerli
pysys.py run -m goerli
```


Running a specific test or range of tests
-----------------------------------------
The [pysys](https://pysys-test.github.io/pysys-test/) launch cli provides a rich interface to allow you to run a 
specific test, ranges of tests, or groups of tests, as well as running them in different modes, with different 
verbosity logging, and in cycles. See the cli documentation for more detail using `pysys.py run -h`. When running tests 
pysys will search the directory tree for all tests available from the current working directory downwards, and then 
filter based on the user request e.g. 


```bash
# run a specific test
pysys.py run gen_cor_001

# run a range of tests (using python list slicing syntax)
pysys.py run gen_cor_001:gen_cor_004
pysys.py run gen_cor_003:

# run a test multiple times
pysys.py run -c 5 gen_cor_003

# run a test with full verbosity logging
pysys.py run -v DEBUG gen_cor_003
```

Whilst pysys does support running tests in a multi-threaded environment, this is currently not supported here due to the 
nonce needing to be synchronised in a single thread when running using the test accounts. This may be changed in the 
future where we partition user accounts across running test groups. 





