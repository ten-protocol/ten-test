const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

async function listenToFilteredSimpleEvent(idFilter, senderFilter) {
    const filter = contract.filters.SimpleEvent(idFilter, null, senderFilter);

    contract.on(filter, (id, message, sender) => {
        console.log(`Filtered SimpleEvent - ID: ${id}, Message: ${message}, Sender: ${sender}`);
    });
}

async function listenToFilteredArrayEvent(idFilter) {
    const filter = contract.filters.ArrayEvent(idFilter);

    contract.on(filter, (id, numbers, messages) => {
        console.log(`Filtered ArrayEvent - ID: ${id}, Numbers: ${numbers}, Messages: ${messages}`);
    });
}

async function listenToFilteredStructEvent(idFilter, userAddressFilter) {
    const filter = contract.filters.StructEvent(idFilter);

    contract.on(filter, (id, user) => {
        if (user.userAddress === userAddressFilter) {
            console.log(`Filtered StructEvent - ID: ${id}, User: ${JSON.stringify(user)}`);
        }
    });
}

async function listenToFilteredMappingEvent(idFilter, keyFilter) {
    const filter = contract.filters.MappingEvent(idFilter);

    contract.on(filter, (id, keys, values) => {
        const index = keys.indexOf(keyFilter);
        if (index !== -1) {
            const value = values[index];
            console.log(`Filtered MappingEvent - ID: ${id}, Key: ${keyFilter}, Value: ${value}`);
        }
    });
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--contract_address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--id_filter <value>', '')
  .option('--address_filter <value>', '')
  .parse(process.argv)

const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)

var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)
const contract = new ethers.Contract(options.contract_address, abi, provider)
const interface = new ethers.utils.Interface(abi)

listenToFilteredSimpleEvent(options.id_filter, options.address_filter);
listenToFilteredArrayEvent(options.id_filter);
listenToFilteredStructEvent(options.id_filter, options.address_filter);
listenToFilteredMappingEvent(options.id_filter, 'transactor%s'%options.id_filter);
console.log("Listening for filtered events...");
