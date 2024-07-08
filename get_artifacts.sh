# script to build artifacts required for running tests 

script_path="$(cd "$(dirname "${0}")" && pwd)"
src_path="${script_path}/../go-ten"

# extract branch and commit hash
cd $src_path
HASH=`git rev-parse HEAD`
BRANCH=`git rev-parse --abbrev-ref HEAD`
cd $script_path

# purge artifacts
echo Purging artifacts directory
rm ${script_path}/artifacts/build.info
rm -rf ${script_path}/artifacts/wallet_extension
rm -rf ${script_path}/artifacts/contracts

# write the build info
echo Creating build info
echo "BRANCH: " $BRANCH > ${script_path}/artifacts/build.info
echo "HASH:   " $HASH  >> ${script_path}/artifacts/build.info
echo "DATE:   " `date` >> ${script_path}/artifacts/build.info
echo "" >> ${script_path}/artifacts/build.info

# run the wallet extension build
echo Building the wallet extension
cd $src_path/tools/walletextension/main

echo Building for target platform
go build -o ${script_path}/artifacts/wallet_extension/wallet_extension .

# run the abigen to create the contract ABIs
cd $src_path/contracts
npm install
npx hardhat compile
npx hardhat generate-abi-bindings --output-dir generated

cd $script_path
cp -r $src_path/contracts/exported/src artifacts/contracts

rm -rf $src_path/contracts/exported/
rm -rf $src_path/contracts/generated/ConstantSupplyERC20/