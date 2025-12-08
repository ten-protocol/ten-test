const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

async function listenToFilteredSimpleEvent(idFilter) {
    const filter = contract.filters.SimpleEvent(idFilter, null, null);

    contract.on(filter, (id, message, sender) => {
        log(`Filtered SimpleEvent - ID: ${id}, Message: ${message}, Sender: ${sender}`);
    });
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--contract_address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--id_filter <value>', 'Id to filter on')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)

var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)
const contract = new ethers.Contract(options.contract_address, abi, provider)
const interface = new ethers.utils.Interface(abi)

listenToFilteredSimpleEvent(options.id_filter);
log(`Listening for filtered events...`);
