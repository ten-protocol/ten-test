const Web3 = require('web3');
const commander = require('commander');
const fs = require('fs');

require('console-stamp')(console, 'HH:MM:ss');

function task1(from) {
  setTimeout(function() {
    contract.getPastEvents('ItemSet1', {
      fromBlock: from,
      toBlock: 'latest',
      filter: {setter: options.filter_address}
    })
    .then(function(events) {
        if (events.length) {
            for (var i = 0, len = events.length; i < len; i+=1) {
                key = events[i].returnValues['key']
                value = events[i].returnValues['value']
                console.log('Task1:', key, value);
                from = events[i].blockNumber+1
            }
        }
        task1(from)
    });
  }, 2000);
}

function task2(from) {
  setTimeout(function() {
    contract.getPastEvents('ItemSet2', {
      fromBlock: from,
      toBlock: 'latest',
      filter: {value: [2,3]}
    })
    .then(function(events) {
        if (events.length) {
            for (var i = 0, len = events.length; i < len; i+=1) {
                key = events[i].returnValues['key']
                value = events[i].returnValues['value']
                console.log('Task2:', key, value);
                from = events[i].blockNumber+1
            }
        }
        task2(from)
    });
  }, 2000);
}

function task3(from) {
  setTimeout(function() {
    contract.getPastEvents('ItemSet3', {
      fromBlock: from,
      toBlock: 'latest',
       topics: [web3.utils.sha3('ItemSet3(string,uint256,address)'), web3.utils.sha3(options.filter_key)
       ]
    })
    .then(function(events) {
        if (events.length) {
            for (var i = 0, len = events.length; i < len; i+=1) {
                value = events[i].returnValues['value']
                console.log('Task3:', value);
                from = events[i].blockNumber+1
            }
        }
        task3(from)
    });
  }, 2000);
}

function generate_viewing_key() {
  console.log('Generating viewing key for', options.pk)
  console.log(options.url_http + '/generateviewingkey/')

  fetch(url+'/generateviewingkey/', {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify({address: account.address})
  })
  .then(response => response.text())
  .then((response) => {
         sign_viewing_key()
   })
}

function sign_viewing_key() {
  console.log('Signing viewing key for', options.pk)
  console.log('Result was', response)
  signed_msg = web3.eth.accounts.sign('vk' + response, '0x' + options.pk)

  fetch(options.url_http + '/submitviewingkey/', {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify( {signature: signed_msg.signature, address: account.address})
  })
  .then(response => response.text())
  .then((response) => {
    console.log('Starting task ...')
    task1(0)
    task2(0)
    task3(0)
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
  .option('-k, --filter_key <value>', 'The key to filter on')
  .option('-p, --pk <value>', 'Private key for this client')
  .option('-o, --obscuro', 'True if running against obscuro', false)
  .parse(process.argv);

const options = commander.opts();
console.log('HTTP URL:', `${options.url_http}`);
console.log('WS URL:', `${options.url_ws}`);
console.log('ADR:', `${options.address}`);
console.log('ABI:', `${options.abi}`);
console.log('ADF:', `${options.filter_address}`);
console.log('KF:', `${options.filter_key}`);
console.log('OB:', `${options.obscuro}`);
console.log('PK:', `${options.pk}`);

var json = fs.readFileSync(`${options.abi}`);
var abi = JSON.parse(json);

const web3 = new Web3(`${options.url_ws}`);
const contract = new web3.eth.Contract(abi, `${options.address}`)
const account = web3.eth.accounts.privateKeyToAccount(`${options.pk}`)

if (options.obscuro == true) {
  generate_viewing_key()
}
else {
  console.log('Starting task ...')
  task1(0)
  task2(0)
  task3(0)
}



