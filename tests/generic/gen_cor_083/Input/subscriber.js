const commander = require('commander');
const http = require('http')

function doSubscribe() {
  console.log('Subscribing for event logs')
  topic = web3.utils.sha3('Stored(uint256)');
  const subscription = web3.eth.subscribe('logs',
    {
      topics: [topic],
      address: options.address
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

function doUnsubscribe() {
  console.log('Unsubscribing from event logs')
  subscription.unsubscribe(function(error, success){
    if (success)
        console.log('Successfully unsubscribed!');
  });
}

function createServer(){
  var server = http.createServer(
    function(request, response) {
      if (request.method == 'POST') {
        var body = ''
        request.on('data', function(data) {
          body += data
        })
        request.on('end', function() {
          if (body == 'SUBSCRIBE'){
            doSubscribe()
          } else if (body == 'UNSUBSCRIBE'){
            doUnsubscribe()
          }
          response.writeHead(200, {'Content-Type': 'text/plain'})
          response.end('post received')
        })
      }
    }
  )
  return server
}

function generate_viewing_key() {
  console.log('Generating viewing key for', options.account_private_key)
  console.log(options.network_http + '/generateviewingkey/')

  fetch(options.network_http +'/generateviewingkey/', {
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
  .option('-p, --script_server_port <value>', 'This script listening port for HTTP posts')
  .option('-u, --network_http <value>', 'Http connection URL to the network')
  .option('-w, --network_ws <value>', 'Web socket connection URL to the network')
  .option('-a, --contract_address <value>', 'Address of the contract')
  .option('-p, --account_private_key <value>', 'Private key for the account')
  .option('-o, --is_obscuro', 'True if running against obscuro', false)
  .parse(process.argv);

const options = commander.opts();

// subscription is initially null
const subscription = null

// create the server to listen for subscription instructions
const server = createServer()

const web3 = new Web3(`${options.network_ws}`);
account = web3.eth.accounts.privateKeyToAccount(`${options.account_private_key}`)

if (options.is_obscuro == true) {
  generate_viewing_key()
  server.listen(options.port, '127.0.0.1')
  console.log('Subscriber listening for instructions')
}
else {
  server.listen(options.port, '127.0.0.1')
  console.log('Subscriber listening for instructions')
}