async function main() {
  const IncrementerV1 = await ethers.getContractFactory("IncrementerV1");
  const incrementerV1 = await upgrades.deployProxy(IncrementerV1);
  await incrementerV1.waitForDeployment();
  console.log("Incrementer proxy deployed to:", await incrementerV1.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
