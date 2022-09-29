const Web3 = require('web3');
const commander = require('commander');
const fs = require('fs');

require('console-stamp')(console, 'HH:MM:ss');

function task1(contract, filter_address, from) {
  setTimeout(function() {
    contract.getPastEvents('ItemSet1', {
      fromBlock: from,
      toBlock: 'latest',
      filter: {setter: filter_address}
    })
    .then(function(events) {
        if (events.length) {
            for (var i = 0, len = events.length; i < len; i+=1) {
                key = events[i].returnValues['key']
                value = events[i].returnValues['value']
                console.log('ItemSet1:', key, value);
                from = events[i].blockNumber+1
            }
        }
        task1(contract, filter_address, from)
    });
  }, 2000);
}

function task2(contract, filter_address, from) {
  setTimeout(function() {
    contract.getPastEvents('ItemSet1', {
      fromBlock: from,
      toBlock: 'latest',
      filter: {value: [2,3]}
    })
    .then(function(events) {
        if (events.length) {
            for (var i = 0, len = events.length; i < len; i+=1) {
                key = events[i].returnValues['key']
                value = events[i].returnValues['value']
                console.log('ItemSet2:', key, value);
                from = events[i].blockNumber+1
            }
        }
        task2(contract, filter_address, from)
    });
  }, 2000);
}

function generate_viewing_key(web3, contract, url, account, private_key) {
  console.log('Generating viewing key for', private_key)
  console.log(url+'/generateviewingkey/')

  fetch(url+'/generateviewingkey/', {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify({address: account.address})
  })
  .then(response => response.text())
  .then((response) => {
         sign_viewing_key(web3, contract, url, account, private_key, response)
   })
}

function sign_viewing_key(web3, contract, url, account, private_key, response) {
  console.log('Signing viewing key for', private_key)
  console.log('Result was', response)
  signed_msg = web3.eth.accounts.sign('vk' + response, '0x' + private_key)

  fetch(url+'/submitviewingkey/', {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify( {signature: signed_msg.signature, address: account.address})
  })
  .then(response => response.text())
  .then((response) => {
    console.log('Starting task ...')
    task1(contract, 0)
    task2(contract, 0)
   })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('-u, --url_http <url>', 'Http connection URL')
  .option('-w, --url_ws <url>', 'Web socket connection URL')
  .option('-a, --address <value>', 'Address of the contract')
  .option('-b, --abi <value>', 'Abi of the contract')
  .option('-f, --filter_address <value>', 'The address to filter on')
  .option('-p, --pk <value>', 'Private key for this client')
  .option('-o, --obscuro', 'True if running against obscuro', false)
  .parse(process.argv);

const options = commander.opts();
console.log('HTTP URL:', `${options.url_http}`);
console.log('WS URL:', `${options.url_ws}`);
console.log('ADR:', `${options.address}`);
console.log('ABI:', `${options.abi}`);
console.log('ADF:', `${options.filter_address}`);
console.log('OB:', `${options.obscuro}`);
console.log('PK:', `${options.pk}`);

const json = fs.readFileSync(`${options.abi}`);
const abi = JSON.parse(json);

const web3 = new Web3(`${options.url_ws}`);
const contract = new web3.eth.Contract(abi, `${options.address}`)
account = web3.eth.accounts.privateKeyToAccount(`${options.pk}`)

if (options.obscuro == true) {
  generate_viewing_key(web3, contract, options.url_http, account, options.pk)
}
else {
  console.log('Starting task ...')
  task1(contract, options.filter_address, 0)
  task2(contract, 0)
}



