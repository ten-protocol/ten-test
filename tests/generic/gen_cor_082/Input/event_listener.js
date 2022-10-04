const Web3 = require('web3');
const commander = require('commander');
const fs = require('fs');

require('console-stamp')(console, 'HH:MM:ss');

function task() {
  console.log('Starting task ...')
  topic = web3.utils.sha3('ItemSet3(string,uint256,address)');
  inputs = [{"indexed": true, "name": "key", "type": "string"}, {"indexed": false, "name": "value", "type": "uint256"}, {"indexed": false, "name": "setter", "type": "address"}]
  topics = [ topic, [web3.utils.sha3(options.filter_key1), web3.utils.sha3(options.filter_key2)] ]
  web3.eth.subscribe('logs', {
      topics: topics,
      address: options.address
    },
    function(error, result) {
      if (error) {
        console.log('Error returned is ', error)
      } else {
        result = web3.eth.abi.decodeLog(inputs, result.data, result.topics)
        console.log('Stored value =', result.value)
      }
    }
  )
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
    task()
   })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('-u, --url_http <url>', 'Http connection URL')
  .option('-w, --url_ws <url>', 'Web socket connection URL')
  .option('-a, --address <value>', 'Address of the contract')
  .option('-f, --filter_key1 <value>', 'The first key value to filter on')
  .option('-g, --filter_key2 <value>', 'The second key value to filter on')
  .option('-p, --pk <value>', 'Private key for this client')
  .option('-o, --obscuro', 'True if running against obscuro', false)
  .parse(process.argv);

const options = commander.opts();
console.log('HTTP URL:', `${options.url_http}`);
console.log('WS URL:', `${options.url_ws}`);
console.log('ADR:', `${options.address}`);
console.log('FK1:', `${options.filter_key1}`);
console.log('FK2:', `${options.filter_key2}`);
console.log('PK:', `${options.pk}`);
console.log('OB:', `${options.obscuro}`);

const web3 = new Web3(`${options.url_ws}`);
account = web3.eth.accounts.privateKeyToAccount(`${options.pk}`)

if (options.obscuro == true) {
  generate_viewing_key()
}
else {
  task()
}










