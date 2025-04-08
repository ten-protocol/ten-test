// Module for joining, signing and registering an account this the ten network
// (see below for example usage)
//
const Web3 = require('web3')
const http = require('http')
const ethers = require('ethers')

module.exports = { join,  sign, authenticate}

require('console-stamp')(console, 'HH:MM:ss')

async function join(url) {
    console.log('Joining the network ' + url)
    let response = await fetch(`${url}/join/`, {
        method: 'GET',
        headers: {Accept: "application/json", "Content-Type": "application/json",},
    });
    let token = await response.text();
    console.log('Joined the network with token ' + token);
    return token;
}

async function sign(account, token) {
    console.log('Signing message for registration ' + account.address)
    let wallet = new ethers.Wallet(account.privateKey)
    let domain = {
        name: "Ten",
        version: "1.0",
        chainId: 443,
        verifyingContract: "0x0000000000000000000000000000000000000000"
    };
    let types = {Authentication: [{name: "Encryption Token", type: "address"},],};
    let message = {"Encryption Token": "0x" + token};
    let signed_msg = await wallet._signTypedData(domain, types, message)
    return signed_msg
}

async function authenticate(url, account, token, signed_msg) {
    console.log('Authenticating account ' + account.address)
    response = await fetch(`${url}/authenticate/?token=${token}`, {
        method: 'POST',
        headers: {Accept: "application/json", "Content-Type": "application/json",},
        body: JSON.stringify({signature: signed_msg, address: account.address})
    })
    let text = await response.text()
    console.log('Authentication response was ' + text)
}

// Example usage ... uncomment to run against the ten sepolia network
//
//  base_url = 'https://testnet.ten.xyz/v1'
//  account = (new Web3()).eth.accounts.create()
//
//  join(base_url).then(token => {
//    sign(account, token).then(signed_msg => {
//      authenticate(base_url, account, token, signed_msg).then(() => {
//        console.log('Completed joining account')
//      })
//    })
//  })