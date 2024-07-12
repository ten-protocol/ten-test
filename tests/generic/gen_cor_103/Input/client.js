const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

async function sendTransaction() {
  const gasPrice = await provider.getGasPrice()
  log(`Wallet address: ${wallet.address}`)
  log(`Gas Price: ${gasPrice}`)

  const tx = {
    to: options.to,
    value: parseInt(options.amount),
    gasLimit: 21000,
    gasPrice: gasPrice,
  }
  log(`Transaction created`)

  const estimateGas = await provider.estimateGas(tx)
  log(`Gas estimate: ${estimateGas}`)
  tx.gasLimit = estimateGas

  const txResponse = await wallet.sendTransaction(tx)
  log(`Transaction sent: ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  log(`Transaction status: ${txReceipt.status}`)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network <value>', 'Connection URL to the network')
  .option('--private_key <value>', 'The account private key')
  .option('--to <value>', 'The address to send funds to')
  .option('--amount <value>', 'The amount of funds to send')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
const provider = new ethers.providers.JsonRpcProvider(options.network)
const wallet = new ethers.Wallet(options.private_key, provider)

log(`Starting transactions`)
sendTransaction().then(() => log(`Completed transactions`));

