const Web3 = require('web3');
const url = 'wss://ws-nd-123-456-789.p2pify.com/3c6e0b8a9c15224a8228b9a98ca1531';
const web3 = new Web3(url);

var options = {
reconnect: {
         auto: true,
         delay: 5000, // ms
         maxAttempts: 5,
         onTimeout: false
},
address: '0x514910771af9ca656af840dff83e8264ecf986ca',
topics: [
 '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
]
};

var subscription = web3.eth.subscribe('logs', options, function(error, result){
    if (!error) console.log('got result');
    else console.log(error);
}).on("data", function(log){
    console.log('got data', log);
}).on("changed", function(log){
    console.log('changed');
});