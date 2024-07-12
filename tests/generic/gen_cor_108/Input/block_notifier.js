const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

var block_count = 0

async function getBlock(blockNumber)  {
  var block = await provider.getBlock(blockNumber);
  log(`Block = ${block}`)
  block_count = block_count + 1
  if (block_count >=4) {
    log(`Switching off subscriptions for newHeads`)
    provider.off("block")
  }
}

function task() {
  log(`Starting task ...`)
  provider.on("block", (blockNumber) => {
    getBlock(blockNumber)
  });
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)
task()


