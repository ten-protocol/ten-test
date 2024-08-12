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
if [ -d ${script_path}/artifacts ]; then
  rm -rfv ${script_path}/artifacts
fi
mkdir ${script_path}/artifacts

# write the build info
echo Creating build info
echo "BRANCH: " $BRANCH > ${script_path}/artifacts/build.info
echo "HASH:   " $HASH  >> ${script_path}/artifacts/build.info
echo "DATE:   " `date` >> ${script_path}/artifacts/build.info
echo "" >> ${script_path}/artifacts/build.info

# run the wallet extension build
echo Building the wallet extension
cd $src_path/tools/walletextension/main

echo Building wallet extension for target platform
go build -o ${script_path}/artifacts/wallet_extension/wallet_extension .

echo Building wallet extension for GOOS=darwin GOARCH=amd64
env GOOS=darwin GOARCH=amd64 go build -o ${script_path}/artifacts/wallet_extension/wallet_extension_macos_amd64 .

echo Building wallet extension for GOOS=darwin GOARCH=arm64
env GOOS=darwin GOARCH=arm64 go build -o ${script_path}/artifacts/wallet_extension/wallet_extension_macos_arm64 .

echo Building wallet extension for GOOS=windows GOARCH=amd64
env GOOS=windows GOARCH=amd64 go build -o ${script_path}/artifacts/wallet_extension/wallet_extension_win_amd64.exe .

echo Building wallet extension for GOOS=linux GOARCH=amd64
env GOOS=linux GOARCH=amd64 go build -o ${script_path}/artifacts/wallet_extension/wallet_extension_linux_amd64

# run the abigen to create the contract ABIs
echo Building the contract ABIs
cd $src_path/contracts
npm install
npx hardhat compile
npx hardhat generate-abi-bindings --output-dir generated

cd $script_path
cp -r $src_path/contracts/exported/src artifacts/contracts

rm -rf $src_path/contracts/exported/
rm -rf $src_path/contracts/generated/ConstantSupplyERC20/