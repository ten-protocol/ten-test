const ethers = require('ethers')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

function mined(tx) {
  provider.once(tx, (transaction) => {
    console.log('Mined', transaction.transactionHash)
  });
}

function pending() {
  console.log('Starting task ...')
  provider.on("pending", (tx) => {
    console.log('Pending', tx)
    mined(tx)
  });
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .parse(process.argv)

const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)
pending()


