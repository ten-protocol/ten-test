async function main() {
  const instance = await ethers.deployContract("Game");
  await instance.waitForDeployment();
  console.log("Contract deployed at", instance.target);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
