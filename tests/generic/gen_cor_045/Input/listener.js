const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

function updateAllowance(allowance) {
  console.log(`Allowance is ${ethers.utils.formatEther(allowance)} OGG`)
}

function displayMessage(msg) {
  console.log(msg)
}

function task() {
  console.log('Starting task ...')

  filterApproval = erc_contract.filters.Approval()
  filterCorrect = game_contract.filters.Correct()
  filterIncorrect = game_contract.filters.Incorrect()
  filterSame = game_contract.filters.Same()
  filterWarmer = game_contract.filters.Warmer()
  filterColder = game_contract.filters.Colder()

  erc_contract.on(filterApproval, (owner, _, value, event) => {
      updateAllowance(value)
      displayMessage(`Approval of ${ethers.utils.formatEther(value)} OGG by account ${owner} to the game was successful. `)
  })
  game_contract.on(filterCorrect, (_, guess, prize, allowance, event) => {
      updateAllowance(allowance)
      displayMessage(`Congratulations! Your guess of ${guess} has won you the prize of ${ethers.utils.formatEther(prize)} OGG.`)
  })
  game_contract.on(filterIncorrect, (_, guess, prize, allowance, event) => {
      updateAllowance(allowance)
      displayMessage(`Sorry! Your guess of ${guess} was wrong. If you try again, we'll tell you whether you're getting warmer. The prize pool of ${ethers.utils.formatEther(prize)} OGG is still up for grabs!`)
  })
  game_contract.on(filterSame, (_, guess, prize, allowance, event) => {
      updateAllowance(allowance)
      displayMessage(`Keep going! Your guess of ${guess} was as far from the correct value as your previous try. Your allowance is ${ethers.utils.formatEther(allowance)} and the prize pool of ${ethers.utils.formatEther(prize)} OGG is still up for grabs!`)
  })
  game_contract.on(filterWarmer, (_, guess, prize, allowance, event) => {
      updateAllowance(allowance)
      displayMessage(`Looking good! Your guess of ${guess} was closer that your previous try. Your allowance is ${ethers.utils.formatEther(allowance)} and the prize pool of ${ethers.utils.formatEther(prize)} OGG is still up for grabs!`)
  })
  game_contract.on(filterColder, (_, guess, prize, allowance, event) => {
      updateAllowance(allowance)
      displayMessage(`Uh oh. Your guess of ${guess} was worse than your previous try. Take heart! Your allowance is ${ethers.utils.formatEther(allowance)} and the prize pool is ${ethers.utils.formatEther(prize)} OGG.`)
  })

  console.log('Registered all subscriptions')
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_http <value>', 'Http connection URL to the network')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--erc_address <value>', 'ERC20 contract address')
  .option('--erc_abi <value>', 'Path to the ERC20 ABI')
  .option('--game_address <value>', 'Guess game contract address')
  .option('--game_abi <value>', 'Path to the Guess game ABI')
  .option('--pk_address <value>', 'The address of the account')
  .parse(process.argv)

const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)

const erc_contract = new ethers.Contract(options.erc_address, JSON.parse(fs.readFileSync(options.erc_abi)), provider)
const game_contract = new ethers.Contract(options.game_address, JSON.parse(fs.readFileSync(options.game_abi)), provider)

task()


