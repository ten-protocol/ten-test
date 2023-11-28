const Web3 = require('web3')
const http = require('http')

module.exports = { register }

async function register(ethereum, host, port, user_id, address, callback) {
    console.log('Registering', address);

    const typedData = {
        types: {
            EIP712Domain: [
                { name: "name", type: "string" },
                { name: "version", type: "string" },
                { name: "chainId", type: "uint256" },
            ],
            Authentication: [
                { name: "EncryptionToken", type: "address" },
            ],
        },
        primaryType: "Authentication",
        domain: {
            name: "Ten",
            version: "1.0",
            chainId: 443,
        },
        message: {
            "EncryptionToken": user_id
        },
    };

    const data = JSON.stringify(typedData);

    let signed_msg;
    try {
        signed_msg = await ethereum.request({
            method: "eth_signTypedData_v4",
            params: [address, data],
        });
    } catch (error) {
        console.log("Signing failed!", error);
        return;
    }

    const response = await fetch(`${host}:${port}/v1/authenticate/?u=${user_id}`, {
        method: 'POST',
        headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
        body: JSON.stringify({ signature: signed_msg, address: address})
    }).then(response => response.text())
      .then((response) => {
        callback()
      });
}