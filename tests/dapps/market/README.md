Market (PUMP) E2E Tests
-----------------------

To run you will need to run the market application in hardhat, and in the test UI obtain funds from the faucet into 
the local fund account as specified in the user.properties file `FundAcntPK` of ten-test. The `market` repo should be 
cloned into the same parent directory as `ten-test` so they are sibling directories. In order for the `FundAcntPK` to 
additionally have an operational role against the contracts, and for the `AAVE` vault to be used as a test vault, the 
following environment arguments should be set.

```bash
export OPERATOR_ADDRESS = <fund account address>
export USE_AAVE_VAULT = false
```

In the `market` directory, to then start up the application, in three separate terminals use;

```bash
yarn chain                     # terminal 1
yarn deploy --network local    # terminal 2
yarn start                     # terminal 2
```

The first command starts up a hardhat network. The second builds and deploys the application. The third starts the 
demo user interface which allows basic interactions into the PUMP contracts. To run the tests you must build the 
artifacts using the `get_artifacts.sh` script located in the root of the `ten-test` project. 