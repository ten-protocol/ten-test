require("@nomicfoundation/hardhat-toolbox");
require("@openzeppelin/hardhat-upgrades");
require('console-stamp')(console, 'HH:MM:ss')

const { PK, HOST, PORT, TOKEN } = process.env;

module.exports = {
  solidity:  "0.8.19",
  defaultNetwork: "ten",
  networks: {
    ten: {
      chainId: 443,
      url: `${HOST}:${PORT}/v1/${TOKEN}`,
      accounts: [ `0x${PK}` ]
     },
     ganache: {
      chainId: 1337,
      url: `${HOST}:${PORT}`,
      accounts: [ `0x${PK}` ]
    }
  }
};