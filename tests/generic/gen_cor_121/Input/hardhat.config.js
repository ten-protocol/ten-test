require("@nomicfoundation/hardhat-toolbox");
require('console-stamp')(console, 'HH:MM:ss')

const { PK, HOST, PORT, TOKEN, API_KEY } = process.env;

module.exports = {
  solidity:  "0.8.7",
  defaultNetwork: "ganache",
  networks: {
    ten: {
      chainId: 443,
      url: `${HOST}:${PORT}/v1/${TOKEN}`,
      gasPrice: 2000000000,
      accounts: [ `0x${PK}` ]
    },
    ganache: {
      chainId: 1337,
      url: `${HOST}:${PORT}`,
      accounts: [ `0x${PK}` ]
    }
  }
};