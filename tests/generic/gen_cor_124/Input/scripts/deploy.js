const { ethers, upgrades } = require("hardhat");

async function main() {
  const [ deployOwner, transferOwner ] = await ethers.getSigners()

  const StoreV1 = await ethers.getContractFactory("StoreV1")
  const proxy = await upgrades.deployProxy(StoreV1, [], { initializer: "initialize" })
  await proxy.waitForDeployment()
  const address = await proxy.getAddress()
  console.log("Proxy deployed at", address)

  await upgrades.admin.transferProxyAdminOwnership( address, transferOwner.address )
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
