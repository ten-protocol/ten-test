Market (PUMP) E2E Tests
-----------------------

To run you will need to run the market application in hardhat, and in the test UI obtain funds from the faucet into 
the local fund account as specified in the user.properties file `FundAcntPK` of ten-test. The `market` repo should be 
cloned into the same parent directory as `ten-test` so they are sibling directories. In the `market` directory, in 
three separate terminals use;

```bash
yarn chain                     # terminal 1
yarn deploy --network local    # terminal 2
yarn start                     # terminal 2
```

The first command starts up a hardhat network. The second builds and deploys the application. The third starts the 
demo user interface which allows basic interactions into the PUMP contracts. 