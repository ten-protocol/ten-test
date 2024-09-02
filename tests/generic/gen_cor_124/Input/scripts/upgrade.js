const { ethers, upgrades } = require("hardhat");

async function main() {
  const address = process.env.ADDRESS;
  console.log("Proxy address passed to main:", address);

  const StoreV2 = await ethers.getContractFactory("StoreV2");
  const storev2 = await upgrades.upgradeProxy(address, StoreV2);
  console.log("StoreV2 deployed to:", await storev2.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
