# script to build artifacts required for running tests 

script_path="$(cd "$(dirname "${0}")" && pwd)"
src_path="${script_path}/../go-obscuro"

# purge artifacts
echo Purging artifacts directory
rm ${script_path}/artifacts/wallet_extension*

# run the build
cd $src_path/tools/walletextension/main
echo Building for target platform
go build -o ${script_path}/artifacts/wallet_extension .

