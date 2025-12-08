const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

function task() {
  log('Starting task ...')

  game_contract.on(game_contract.filters.Guessed(), (_, guess, success, secret, event) => {
      log(`Your guess of ${guess} had success ${success} ... secret is ${secret}`)
  })

  log('Registered all subscriptions')
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--game_address <value>', 'Guess game contract address')
  .option('--game_abi <value>', 'Path to the Guess game ABI')
  .option('--pk_address <value>', 'The address of the account')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)
const game_contract = new ethers.Contract(options.game_address, JSON.parse(fs.readFileSync(options.game_abi)), provider)
task()


