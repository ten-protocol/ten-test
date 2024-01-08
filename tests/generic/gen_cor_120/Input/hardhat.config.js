require("@nomicfoundation/hardhat-toolbox");

const { ACCOUNT_PK, GW_PORT, GW_TOKEN } = process.env;

module.exports = {
  solidity:  "0.8.7",
  defaultNetwork: "hardhat",
  networks: {
    ten_local: {
      deploy: [ "scripts/" ],
      chainId: 443,
      url: `http://127.0.0.1:${GW_PORT}/v1/${GW_TOKEN}`,
      gasPrice: 2000000000,
      accounts: [ `0x${ACCOUNT_PK}` ]
    },
    hardhat: {
      deploy: [ "scripts/" ],
      chainId: 1337,
      accounts: [
        { "privateKey": `0x${APP_DEV_PK}`,  "balance": "174165200000000000" }
      ]
    }
  }
};