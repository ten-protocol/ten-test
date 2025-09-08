require("@nomicfoundation/hardhat-toolbox");
require("@tenprotocol/ten-hardhat-plugin")
require('console-stamp')(console, 'HH:MM:ss')

const { PK, CHAINID, HOST, PORT } = process.env;

module.exports = {
  solidity:  "0.8.19",
  defaultNetwork: "ten",
  networks: {
    ten: {
      deploy: [ "scripts/" ],
      chainId: ${CHAINID},
      url: `${HOST}:${PORT}/v1/`,
      useGateway: true,
      accounts: [ `0x${PK}` ]
    }
  }
};