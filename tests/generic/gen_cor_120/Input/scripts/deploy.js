const hre = require("hardhat");
require('console-stamp')(console, 'HH:MM:ss')

async function main() {

  // deployment without using a factory
  const instance = await hre.ethers.deployContract("Double");
  await instance.waitForDeployment();
  console.log("Contract deployed at", instance.target);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
