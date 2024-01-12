require("@nomicfoundation/hardhat-toolbox");

const { PK, HOST, PORT, TOKEN, API_KEY } = process.env;

module.exports = {
  solidity:  "0.8.7",
  defaultNetwork: "ganache",
  networks: {
    ten: {
      deploy: [ "scripts/" ],
      chainId: 443,
      url: `${HOST}:${PORT}/v1/${TOKEN}`,
      gasPrice: 2000000000,
      accounts: [ `0x${PK}` ]
    },
    sepolia: {
      deploy: [ "scripts/" ],
      chainId: 11155111,
      url: `${HOST}/${API_KEY}`,
      gasPrice: 34254316565,
      accounts: [ `0x${PK}` ]
    },
    ganache: {
      deploy: [ "scripts/" ],
      chainId: 1337,
      url: `${HOST}:${PORT}`,
      accounts: [ `0x${PK}` ]
    }
  }
};