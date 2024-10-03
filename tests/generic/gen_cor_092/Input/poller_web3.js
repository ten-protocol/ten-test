const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

async function task(network_http, network_ws, chainId, address, abi) {
  try {
   const web3 = new Web3(`${network_http}`)
   const contract = new web3.eth.Contract(abi, address)
   contract.getPastEvents('Stored', { fromBlock: 0, toBlock: 'latest'})
    .then(function(events) {
        if (events.length) {
            for (var i = 0, len = events.length; i < len; i+=1) {
                log('Stored value = ' + events[i].returnValues['value'])
                log('Block number of event log is ' + events[i].blockNumber)
                from = events[i].blockNumber+1
            }
        }
    });
  } catch (error) {
    console.error('Error fetching events:', error);
  }
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_http <value>', 'HTTP connection URL to the network')
  .option('--network_ws <value>', 'Websocket connection URL to the network')
  .option('--chain_id <value>', 'The network chain ID')
  .option('--contract_address <value>', 'The contract address')
  .option('--contract_abi <value>', 'The contract ABI file')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
var json = fs.readFileSync(`${options.contract_abi}`)
var abi = JSON.parse(json)
task(options.network_http, options.network_ws, options.chain_id, options.contract_address, abi);


