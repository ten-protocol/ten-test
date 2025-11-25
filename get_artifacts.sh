# script to build artifacts required for running tests 

script_path="$(cd "$(dirname "${0}")" && pwd)"
go_ten="${script_path}/../go-ten"
market="${script_path}/../market"

# purge the artifacts directory
echo Purging artifacts directory
if [ -d ${script_path}/artifacts ]; then
  rm -rfv ${script_path}/artifacts
fi
mkdir ${script_path}/artifacts
mkdir ${script_path}/artifacts/go-ten
mkdir ${script_path}/artifacts/market

# -------------------------------------------------
# Build the go-ten repo artifacts
# -------------------------------------------------
if [ -d $go_ten ]; then
  echo Creating go-ten build info
  cd $go_ten
  HASH=`git rev-parse HEAD`
  BRANCH=`git rev-parse --abbrev-ref HEAD`
  cd $script_path
  echo "BRANCH: " $BRANCH > ${script_path}/artifacts/go-ten/build.info
  echo "HASH:   " $HASH  >> ${script_path}/artifacts/go-ten/build.info
  echo "DATE:   " `date` >> ${script_path}/artifacts/go-ten/build.info
  echo "" >> ${script_path}/artifacts/go-ten/build.info

  # run the wallet extension build
  echo Building the wallet extension
  cd $go_ten/tools/walletextension/main

  echo Building wallet extension for target platform
  go build -o ${script_path}/artifacts/go-ten/wallet_extension/wallet_extension .

  echo Building wallet extension for GOOS=darwin GOARCH=amd64
  env GOOS=darwin GOARCH=amd64 go build -o ${script_path}/artifacts/go-ten/wallet_extension/wallet_extension_macos_amd64 .

  echo Building wallet extension for GOOS=darwin GOARCH=arm64
  env GOOS=darwin GOARCH=arm64 go build -o ${script_path}/artifacts/go-ten/wallet_extension/wallet_extension_macos_arm64 .

  echo Building wallet extension for GOOS=windows GOARCH=amd64
  env GOOS=windows GOARCH=amd64 go build -o ${script_path}/artifacts/go-ten/wallet_extension/wallet_extension_win_amd64.exe .

  echo Building wallet extension for GOOS=linux GOARCH=amd64
  env GOOS=linux GOARCH=amd64 go build -o ${script_path}/artifacts/go-ten/wallet_extension/wallet_extension_linux_amd64

  # run the abigen in go-ten to create the contract ABIs and copy over
  echo Building the go-ten contract ABIs
  cd $go_ten/contracts
  npm install
  npx hardhat compile
  npx hardhat generate-abi-bindings --output-dir generated
  cd $script_path
  cp -r $go_ten/contracts/exported/src artifacts/go-ten/contracts
  rm -rf $go_ten/contracts/exported/
  rm -rf $go_ten/contracts/generated/ConstantSupplyERC20/

fi

# -------------------------------------------------
# Build the market repo artifacts
# -------------------------------------------------
if [ -d $market ]; then
  echo Creating market build info
  cd $market
  HASH=`git rev-parse HEAD`
  BRANCH=`git rev-parse --abbrev-ref HEAD`
  cd $script_path
  echo "BRANCH: " $BRANCH > ${script_path}/artifacts/market/build.info
  echo "HASH:   " $HASH  >> ${script_path}/artifacts/market/build.info
  echo "DATE:   " `date` >> ${script_path}/artifacts/market/build.info
  echo "" >> ${script_path}/artifacts/market/build.info

  # copy the market dApp contract abi (assumes the application has been started up externally)
  echo Copying the market dApp contract ABIs if they exist
  if [ -d $market/packages/hardhat/artifacts/contracts ]; then
    cp -r $market/packages/hardhat/artifacts/contracts artifacts/market/contracts
  fi

fi
