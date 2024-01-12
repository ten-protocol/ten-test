const hre = require("hardhat");

async function main() {

  // deployment without using a factory
  const instance = await hre.ethers.deployContract("Double");
  await instance.waitForDeployment();
  console.log("Contract deployed at", instance.target);

  // deployment using a factory
  //  const factory = await hre.ethers.getContractFactory("Double");
  //  const instance = await factory.deploy()
  //  await instance.waitForDeployment();
  //  console.log("Contract deployed at", instance.target);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
