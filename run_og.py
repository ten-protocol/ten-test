import json, requests, secrets
from web3 import Web3
from eth_account.messages import encode_defunct


class GatewayTester:
    host = '127.0.0.1'
    port = 3000

    @classmethod
    def run(cls):
        pk = secrets.token_hex(32)
        account = Web3().eth.account.privateKeyToAccount(pk)
        print('Running for account', account.address)

        user_id = cls.join()
        print('Registered user id', user_id)

        url = '%s:%d/?u=%s' % (cls.host, cls.port, user_id)
        web3 = Web3(Web3.HTTPProvider(url))
        print('Connection urls', user_id)

        response = cls.register(web3, pk, account, user_id)
        print('Register response', response.text)

        web3.eth.get_balance(account.address)

    @classmethod
    def join(cls):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.get('http://%s:%d/join/' % (cls.host, cls.port),  headers=headers)
        return response.text

    @classmethod
    def register(cls, web3, pk, account, user_id):
        text_to_sign = "Register " + user_id + " for " + account.address
        signed_msg = web3.eth.account.sign_message(encode_defunct(text=text_to_sign), private_key=pk)

        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        data = {"signature": signed_msg.signature.hex(), "message": text_to_sign}
        response = requests.post('http://%s:%d/authenticate/?u=%s' % (cls.host, cls.port, user_id), data=json.dumps(data), headers=headers)
        return response


if __name__ == '__main__':
    GatewayTester.run()