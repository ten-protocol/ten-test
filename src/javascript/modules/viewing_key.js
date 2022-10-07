const Web3 = require('web3')
const http = require('http')

module.exports = { generate_viewing_key,  sign_viewing_key }

function generate_viewing_key(web3, network_url, address, private_key, callback) {
  console.log('Generating viewing key for', private_key)
  console.log(network_url + '/generateviewingkey/')

  fetch(network_url +'/generateviewingkey/', {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify({address: address})
  })
  .then(response => response.text())
  .then((response) => {
         sign_viewing_key(web3, network_url, address, private_key, callback, response)
   })
}

function sign_viewing_key(web3, network_url, address, private_key, callback, response) {
  console.log('Signing viewing key for', private_key)
  signed_msg = web3.eth.accounts.sign('vk' + response, '0x' + private_key)

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