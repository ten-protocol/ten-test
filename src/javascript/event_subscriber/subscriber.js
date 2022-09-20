const Web3 = require('web3');
const commander = require('commander');

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('-u, --url <url>', 'The node WSS endpoint.')
  .option('-a, --address <value>', 'the address of the contract whose events you subscribe to.', 'Default')
  .option('-k, --event <value>', 'The Keccak-256 value of the event.', 'Default')
  .parse(process.argv);

const options = commander.opts();
console.log('URL:', `${options.url}`);
console.log('Address:', `${options.address}`);
console.log('Event:', `${options.event}`);

const web3 = new Web3(`${options.url}`);

var subscription_options = {
reconnect: {
         auto: true,
         delay: 5000,
         maxAttempts: 5,
         onTimeout: false
},
address: `${options.address}`,
topics: [
 `${options.event}`
]
};

var subscription = web3.eth.subscribe('logs', subscription_options, function(error, result){
    if (!error) console.log('got result');
    else console.log(error);
}).on("data", function(log){
    console.log('got data', log);
}).on("changed", function(log){
    console.log('changed');
});