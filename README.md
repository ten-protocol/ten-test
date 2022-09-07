<h1 align="center">
  <img alt="obscuro logo" src="https://github.com/obscuronet/obscuro-test/blob/main/.assets/logo_fade.gif" width="720px"/>
  Obscuro Test Framework 
</h1>

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
![Python](https://img.shields.io/badge/python-3.9-blue.svg)
[![Run local tests](https://github.com/obscuronet/obscuro-test/actions/workflows/local_tests.yml/badge.svg)](https://github.com/obscuronet/obscuro-test/actions/workflows/local_tests.yml)
[![Run testnet tests](https://github.com/obscuronet/obscuro-test/actions/workflows/testnet_tests.yml/badge.svg)](https://github.com/obscuronet/obscuro-test/actions/workflows/testnet_tests.yml)

Project repo for running end to end system tests against a variety of networks, with [obscuro](https://obscu.ro/) being 
the primary network under test. Other networks supported include [ganache](https://trufflesuite.com/ganache/), 
[ropsten via infura](https://infura.io/), and [geth](https://geth.ethereum.org/docs/getting-started). The repo uses the 
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
│    └── python          # The python source root for pysys extensions
├── tests                # The test root for all tests 
│    ├── generic         # Network agnostic tests 
│    └── obscuro         # Obscuro specific tests 
└── utils                # The project utils root for utilities used by the tests
     ├── contracts       # A library of smart contracts 
     └── docker          # Docker configuration and build files 
```

The [.default.properties](./.default.properties) file contains properties for running the tests that are common to any 
user. User specific properties should be added into a `.username.properties` file at the root of the project. As this 
file could contain sensitive data it should never be committed back into the main repo (the [.gitignore](./.gitignore) 
should prevent this). Properties will first be looked for in a `.username.properties` should it exist, and if not will 
fall back to the default properties. 


Quickstart Setup and Run
------------------------
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

Pre-setup required for Obscuro
------------------------------
Whilst the repo is set up to run against a variety of different networks, to run against Obscuro some specific setup 
tasks are required. This is because currently we need to allocate native OBX for gas usage to all test user accounts, and 
also for Obscuro specific tests which require tokens to be available in well known ERC20 contracts. To allocate these
you must first change directory into the `obscuro-test\admin` directory and run the below;

```bash
# to allocate on Obscuro testnet
pysys.py run fund_deploy_native
pysys.py run fund_deploy_tokens
pysys.py run fund_test_users

# to allocate on Obscuro dev-testnet
pysys.py run -m obscuro.dev fund_deploy_native
pysys.py run -m obscuro.dev fund_deploy_tokens
pysys.py run -m obscuro.dev fund_test_users
```

See [admin\README.md](admin\README.md]) for more details. 

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

# run the tests against a local ganache network 
pysys.py run -m ganache
```

To run the same tests against Ropsten, a `.username.properties` file should be created in the root of the working 
directory of the project (where `username` is the output of running `whoami`), and the following properties should be added 
as based on details relevant to the user; 

```
[all]
Account1PK=<private key of account 1 available e.g. via metamask>
Account2PK=<private key of account 2>
Account3PK=<private key of account 3>
GameUserPK=<private key of account 4>

[ropsten]
ProjectID=<project ID>
```

These need to be real accounts to run on Ropsten, whereas for Ganache and Obscuro, currently default ones can be used 
as detailed in [.default.properties](./.default.properties). To run the tests against Ropsten use;

```bash
# run the tests against ropsten
pysys.py run -m ropsten
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




