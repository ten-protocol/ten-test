const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

async function sendTransaction() {
  const gasPrice = await provider.getGasPrice();

  const tx = await contract.populateTransaction.setItem(options.key, options.value, {
    from: wallet.address,
    gasPrice: gasPrice,
    gasLimit: 100000,
  } )
  log(`Transaction created`)

  const txResponse = await wallet.sendTransaction(tx)
  log(`Transaction sent: ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  log(txReceipt)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network <value>', 'Connection URL to the network')
  .option('--address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--private_key <value>', 'The account private key')
  .option('--key <value>', 'The key to store against')
  .option('--value <value>', 'The value to store against the key')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)

const provider = new ethers.providers.JsonRpcProvider(options.network)
const wallet = new ethers.Wallet(options.private_key, provider)
const contract = new ethers.Contract(options.address, abi, wallet)

log(`Starting transactions`)
sendTransaction().then(() => log(`Completed transactions`));

