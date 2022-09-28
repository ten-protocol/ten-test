const Web3 = require('web3');
const commander = require('commander');
const fs = require('fs');

require('console-stamp')(console, 'HH:MM:ss');

function generate_viewing_key(web3, contract, url, account, private_key) {
  console.log('Generating viewing key for', private_key)

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
    console.log('Starting to run the polling loop')
    get_balance(contract, account.address)
   })
}

function get_balance(contract, address) {
  web3.eth.getBalance(account.address,
    function(error, result) {
      if (error) {
        console.log('Error returned is ', error)
      } else {
        //this should only pass if the viewing key was registered successfully
        console.log('Account balance is', result)
        console.log('Starting to run the polling loop')
        task(contract, account.address);
      }
    }
  )
}

function task(contract, address) {
  setTimeout(function() {
    contract.methods.balanceOf(address).call(
      function(error, result) {
        if (error) {
          console.log('Error returned is ', error)
        } else {
          console.log('New balance =', result)
          task(contract, address);
        }
     })
  }, 2000);
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('-u, --url <url>', 'Connection URL')
  .option('-a, --address <value>', 'Address of the contract')
  .option('-b, --abi <value>', 'Abi of the contract')
  .option('-p, --pk <value>', 'Private key for this client')
  .option('-o, --obscuro', 'True if running against obscuro', false)
  .parse(process.argv);

const options = commander.opts();
console.log('URL:', `${options.url}`);
console.log('ADR:', `${options.address}`);
console.log('ABI:', `${options.abi}`);
console.log('PK:', `${options.pk}`);
console.log('OB:', `${options.obscuro}`);

const json = fs.readFileSync(`${options.abi}`);
const abi = JSON.parse(json);

const web3 = new Web3(`${options.url}`);
const contract = new web3.eth.Contract(abi, `${options.address}`)
account = web3.eth.accounts.privateKeyToAccount(`${options.pk}`)
if (options.obscuro == true) {
  generate_viewing_key(web3, contract, options.url, account, options.pk)
}
else {
  get_balance(contract, account.address)
}







