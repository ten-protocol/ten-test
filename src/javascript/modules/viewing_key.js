const Web3 = require('web3')
const http = require('http')

module.exports = { generate_viewing_key,  sign_viewing_key }

function generate_viewing_key(sign, network_url, address, callback) {
  console.log('Generating viewing key for', address)

  fetch(network_url +'/generateviewingkey/', {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify({address: address})
  })
  .then(response => response.text())
  .then((response) => {
         sign_viewing_key(sign, network_url, address, callback, response)
   })
}

function sign_viewing_key(sign, network_url, address, callback, response) {
  console.log('Signing viewing key for', address)
  signed_msg = sign('vk' + response)

  fetch(network_url + '/submitviewingkey/', {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify( {signature: signed_msg.signature, address: address})
  })
  .then(response => response.text())
  .then((response) => {
    callback()
   })
}