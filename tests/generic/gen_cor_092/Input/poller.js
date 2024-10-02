const fs = require('fs')
const commander = require('commander')
import { createPublicClient, http, getContractEvents, defineChain } from 'viem';

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

function createCustomClient(chain_id, network_http) {
  const customChain = defineChain({
    id: chain_id,
    name: 'Ten',
    network: 'ten',
    nativeCurrency: {
      name: 'Ether',
      symbol: 'ETH',
      decimals: 18,
    },
    rpcUrls: {
      default: { http: [network_http], },
    },
  });

  return createPublicClient({ chain: customChain, transport: http(network_http), });
}

async function task(network_http, address, abi, from) {
  try {
    const client = createCustomClient(network_http);
    const events = await getContractEvents(client, {
      address: address,
      abi: abi,
      fromBlock: BigInt(from),
      toBlock: 'latest',
    });
    log('Past Events:', events);
  } catch (error) {
    console.error('Error fetching events:', error);
  }
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_http <value>', 'HTTP connection URL to the network')
  .option('--contract_address <value>', 'The contract address')
  .option('--contract_abi <value>', 'The contract ABI file')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
var json = fs.readFileSync(`${options.contract_abi}`)
var abi = JSON.parse(json)
task(options.network_http, option.contract_address, abi, 0);



