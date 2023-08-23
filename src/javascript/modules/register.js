const Web3 = require('web3')
const http = require('http')

module.exports = { register }

async function register(sign, host, port, user_id, address, callback) {
    console.log('Registering', address)
    text_to_sign = "Register " + user_id + " for " + address.toLowerCase()
    signed_msg = sign(text_to_sign)

    response = await fetch(host + ':' + port + '/authenticate/?u=' + user_id, {
      method: 'POST',
      headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
      body: JSON.stringify( {signature: signed_msg.signature, message: text_to_sign})
    })
    .then(response => response.text())
    .then((response) => {
      callback()
     })
}