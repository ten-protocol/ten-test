const Web3 = require('web3');
const commander = require('commander');

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('-u, --url <url>', 'Connection URL')
  .option('-a, --address <value>', 'Address of the contract')
  .option('-b, --abi <value>', 'Abi of the contract')
  .option('-p, --pk <value>', 'Private key of account to poll')
  .parse(process.argv);

const options = commander.opts();
console.log('URL:', `${options.url}`);
console.log('ADR:', `${options.address}`);
console.log('ABI:', `${options.abi}`);
console.log('PK:', `${options.pk}`);

const web3 = new Web3(`${options.url}`);

//var subscription_options = {
//reconnect: {
//         auto: true,
//         delay: 5000,
//         maxAttempts: 5,
//         onTimeout: false
//},
//address: `${options.address}`,
//topics: [
// `${options.event}`
//]
//};
//
//var subscription = web3.eth.subscribe('logs', subscription_options, function(error, result){
//    if (!error) console.log('got result');
//    else console.log(error);
//}).on("data", function(log){
//    console.log('got data', log);
//}).on("changed", function(log){
//    console.log('changed');
//});