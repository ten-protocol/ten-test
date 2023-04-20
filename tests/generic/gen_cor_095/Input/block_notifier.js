const ethers = require('ethers')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss.l')

async function getBlock(blockNumber)  {
  var block = await provider.getBlock(blockNumber);
  if (block.transactions.length != 0) {
    block.transactions.forEach(item => console.log(block.number, item))
  }
}

function task() {
  console.log('Starting task ...')
  provider.on("block", (blockNumber) => {
    getBlock(blockNumber)
  });
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .parse(process.argv)

const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)
task()


