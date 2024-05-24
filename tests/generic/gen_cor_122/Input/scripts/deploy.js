const { ethers, upgrades } = require("hardhat");

async function main() {
  const DoubleV1 = await ethers.getContractFactory("DoubleV1");
  const doublev1 = await upgrades.deployProxy(DoubleV1);
  await doublev1.waitForDeployment();
  const address = await doublev1.getAddress()
  console.log("Proxy deployed at", address);

  // @todo comment back in when we support upgrades against proxies
  //const DoubleV2 = await ethers.getContractFactory("DoubleV2");
  //const doublev2 = await upgrades.upgradeProxy(address, DoubleV2);
  //console.log("DoubleV2 deployed to:", await doublev2.getAddress());

}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
