const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

async function listenToFilteredSimpleEvent(idFilter) {
    const filter = contract.filters.SimpleEvent(idFilter, null, null);

    contract.on(filter, (id, message, sender) => {
        console.log(`Filtered SimpleEvent - ID: ${id}, Message: ${message}, Sender: ${sender}`);
    });
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--contract_address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--id_filter <value>', 'Id to filter on')
  .parse(process.argv)

const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)

var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)
const contract = new ethers.Contract(options.contract_address, abi, provider)
const interface = new ethers.utils.Interface(abi)

listenToFilteredSimpleEvent(options.id_filter);
console.log("Listening for filtered events...");
