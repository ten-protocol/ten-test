const Web3 = require('web3');
const commander = require('commander');
const fs = require('fs');

require('console-stamp')(console, 'HH:MM:ss');

function task(web3, topic) {
  console.log('Starting task ...')
  web3.eth.subscribe('logs', {topics: ['0x12345...']},
    function(error, result) {
      if (error) {
        console.log('Error returned is ', error)
      } else {
        console.log('Stored value =', result.returnValues['value']);
      }
    }
  )
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
    task(contract, account.address)
   })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('-u, --url_http <url>', 'Http connection URL')
  .option('-w, --url_ws <url>', 'Web socket connection URL')
  .option('-a, --address <value>', 'Address of the contract')
  .option('-b, --abi <value>', 'Abi of the contract')
  .option('-p, --pk <value>', 'Private key of account to poll')
  .option('-o, --obscuro', 'True if running against obscuro', false)
  .parse(process.argv);

const options = commander.opts();
console.log('HTTP URL:', `${options.url_http}`);
console.log('WS URL:', `${options.url_ws}`);
console.log('ADR:', `${options.address}`);
console.log('ABI:', `${options.abi}`);
console.log('PK:', `${options.pk}`);
console.log('OB:', `${options.obscuro}`);

const json = fs.readFileSync(`${options.abi}`);
const abi = JSON.parse(json);

const web3 = new Web3(`${options.url_ws}`);
const contract = new web3.eth.Contract(abi, `${options.address}`)
account = web3.eth.accounts.privateKeyToAccount(`${options.pk}`)

if (options.obscuro == true) {
  generate_viewing_key(web3, contract, options.url_http, account, options.pk)
}
else {
  task(contract, account.address)
}










