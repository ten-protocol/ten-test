const Web3 = require('web3')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

async function sendTransaction() {
  const gasPrice = await web3.eth.getGasPrice()

  const transactionParameters = {
    from: sender_address,
    to: options.to,
    gas: 21000,
    gasPrice: gasPrice,
    value: options.amount,
    nonce: await web3.eth.getTransactionCount(sender_address),
  }
  console.log('Transaction created')

  const signedTransaction = await web3.eth.accounts.signTransaction(transactionParameters, options.private_key);
  const txReceipt = await web3.eth.sendSignedTransaction(signedTransaction.rawTransaction)
  console.log(`Transaction status: ${txReceipt.status}`)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network <value>', 'Connection URL to the network')
  .option('--private_key <value>', 'The account private key')
  .option('--to <value>', 'The address to send funds to')
  .option('--amount <value>', 'The amount of funds to send')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network}`)
const sender_address = web3.eth.accounts.privateKeyToAccount(options.private_key).address

console.log('Starting transactions')
sendTransaction().then(() => console.log('Completed transactions'));

