
const ethers = require('ethers')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss.l')

var block_count = 0

async function getBlock(blockNumber)  {
  var block = await provider.getBlock(blockNumber);
  console.log('Block =', block)
  block_count = block_count + 1
  if (block_count >=4) {
    console.log('Switching off subscriptions for newHeads')
    provider.off("block")
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


