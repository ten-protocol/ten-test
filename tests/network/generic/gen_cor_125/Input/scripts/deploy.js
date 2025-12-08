const { ethers, upgrades } = require("hardhat");

async function main() {
  const MessageBusV1 = await ethers.getContractFactory("MessageBusV1");
  const messagebusv1 = await upgrades.deployProxy(MessageBusV1, [], {
    initializer: 'initialize',
    kind: 'uups'
   })

  await messagebusv1.waitForDeployment();
  const address = await messagebusv1.getAddress()
  console.log("Proxy deployed at", address);

  const MessageBusV2 = await ethers.getContractFactory("MessageBusV2");
  const messagebusv2 = await upgrades.upgradeProxy(address, MessageBusV2);
  console.log("MessageBusV2 deployed to:", await messagebusv2.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
