async function main() {
  const Incrementer = await ethers.getContractFactory("IncrementerV1");
  const incrementer = await upgrades.deployProxy(Incrementer);
  await incrementer.waitForDeployment();
  console.log("Incrementer proxy deployed to:", await incrementer.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
