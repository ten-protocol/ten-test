
const { PROXY } = process.env;

async function main() {
   console.log(`Incrementer proxy address is: ${PROXY}`);
   const IncrementerV2 = await ethers.getContractFactory("IncrementerV2");
   let incrementerV2 = await upgrades.upgradeProxy(`${PROXY}`, IncrementerV2);
   console.log("Incrementer V2 deployed to:", await incrementerV2.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
