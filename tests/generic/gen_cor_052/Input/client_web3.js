const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

async function sendTransaction() {
  try {
    const functionCall = contract.methods.force_require_non_view('key')
    const gasEstimate = await contract.methods.force_require_non_view('').estimateGas({ from: sender_address })
    const gasPrice = await web3.eth.getGasPrice()

    const transactionParameters = {
      from: sender_address,
      to: options.address,
      gas: gasEstimate,
      gasPrice: gasPrice,
      data: functionCall.encodeABI(),
      nonce: await web3.eth.getTransactionCount(sender_address),
    }
    log('Transaction created')

    const signedTransaction = await web3.eth.accounts.signTransaction(transactionParameters, options.private_key);
    const txReceipt = await web3.eth.sendSignedTransaction(signedTransaction.rawTransaction)
    log(`Transaction status: ${txReceipt.status}`)
  }
  catch(err) {
    log(err)
  }
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network <value>', 'Connection URL to the network')
  .option('--address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--private_key <value>', 'The account private key')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)

const web3 = new Web3(`${options.network}`)
const contract = new web3.eth.Contract(abi, options.address)
const sender_address = web3.eth.accounts.privateKeyToAccount(options.private_key).address

log('Starting transactions')
sendTransaction().then(() => log('Completed transactions'));

