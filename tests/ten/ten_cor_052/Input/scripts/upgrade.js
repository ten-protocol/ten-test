async function main() {
   const IncrementerV2 = await ethers.getContractFactory("IncrementerV2");
   let incrementerV2 = await upgrades.upgradeProxy(UPGRADEABLE_PROXY, IncrementerV2);
   console.log("Incrementer proxy deployed to:", await incrementerV2.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
