const Web3 = require('web3');
const commander = require('commander');
const fs = require('fs');

require('console-stamp')(console, 'HH:MM:ss');

function task() {
  console.log('Starting task ...')
  topic = web3.utils.sha3('Stored(uint256)');
  web3.eth.subscribe('logs', {
      topics: [topic],
      fromBlock: options.from_block
    },
    function(error, result) {
      if (error) {
        console.log('Error returned is ', error)
      } else {
        console.log('Full result is ', result);
        console.log('Stored value =', Web3.utils.hexToNumber(result.data));
      }
    }
  )
}

function generate_viewing_key() {
  console.log('Generating viewing key for', options.pk)
  console.log(options.url_http + '/generateviewingkey/')

  fetch(options.url_http +'/generateviewingkey/', {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify({address: account.address})
  })
  .then(response => response.text())
  .then((response) => {
         sign_viewing_key(response)
   })
}

function sign_viewing_key(response) {
  console.log('Signing viewing key for', options.pk)
  signed_msg = web3.eth.accounts.sign('vk' + response, '0x' + options.pk)

  fetch(options.url_http + '/submitviewingkey/', {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify( {signature: signed_msg.signature, address: account.address})
  })
  .then(response => response.text())
  .then((response) => {
    task()
   })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('-u, --url_http <url>', 'Http connection URL')
  .option('-w, --url_ws <url>', 'Web socket connection URL')
  .option('-k, --from_block <value>', 'The block number to start from')
  .option('-p, --pk <value>', 'Private key for this client')
  .option('-o, --obscuro', 'True if running against obscuro', false)
  .parse(process.argv);

const options = commander.opts();
console.log('HTTP URL:', `${options.url_http}`);
console.log('WS URL:', `${options.url_ws}`);
console.log('FB:', `${options.from_block}`);
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










