const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')


function task() {
  console.log('Starting task ...')
  filter = game_contract.filters.Guessed()

  game_contract.on(filter, (_, guess, success, event) => {
      console.log(`Your guess of ${guess} had success ${success}`)
  })

  console.log('Registered all subscriptions')
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_http <value>', 'Http connection URL to the network')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--game_address <value>', 'Guess game contract address')
  .option('--game_abi <value>', 'Path to the Guess game ABI')
  .option('--pk_address <value>', 'The address of the account')
  .parse(process.argv)

const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)
const game_contract = new ethers.Contract(options.game_address, JSON.parse(fs.readFileSync(options.game_abi)), provider)
task()


