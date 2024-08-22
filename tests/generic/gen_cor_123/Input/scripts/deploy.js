const { ethers, upgrades } = require("hardhat");

async function main() {
  const StoreV1 = await ethers.getContractFactory("StoreV1");
  const storev1 = await upgrades.deployProxy(StoreV1);
  await storev1.waitForDeployment();
  const address = await storev1.getAddress()
  console.log("Proxy deployed at", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
