const fs = require('fs')
const commander = require('commander')
const { createPublicClient, http, webSocket, getContractEvents, defineChain, getAbiItem } = require('viem');


function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

function createCustomClient(network_http, network_ws, chain_id) {
  const customChain = defineChain({
    id: chain_id,
    name: 'test',
    network: 'test',
    nativeCurrency: {
      name: 'Ether',
      symbol: 'ETH',
      decimals: 18,
    },
    rpcUrls: {
      default: {
        http: [network_http],
        webSocket: [network_ws],
      },
    },
  });

  return createPublicClient({ chain: customChain, transport: http(network_http), });
}

async function task(network_http, network_ws, chainId, address, abi) {
  try {
    const client = createCustomClient(network_http, network_ws, chainId);
    const logs = await client.getLogs({
      address: address,
      fromBlock: 0,
      toBlock: 'latest',
      topics: ['0xc6d8c0af6d21f291e7c359603aa97e0ed500f04db6e983b9fce75a91c6b8da6b'],
    });
    log('Raw Events:', logs);

    const decodedEvents = logs.map(log => {
      const abiItem = getAbiItem({ abi: abi, name: log.name });
      return {
        ...log,
        decoded: abiItem ? abiItem.decode(log.data) : null,
      };
    });

    log('Decoded Events:', decodedEvents);
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



