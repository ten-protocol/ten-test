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

        response = cls.connect(account, user_id)
        print('Register response', response.text)

        url = 'http://%s:%d/?u=%s' % (cls.host, cls.port, user_id)
        web3 = Web3(Web3.HTTPProvider(url))
        balance = web3.eth.get_balance(account.address)
        print(balance)

    @classmethod
    def join(cls):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.get('http://%s:%d/join/' % (cls.host, cls.port),  headers=headers)
        return response.text

    @classmethod
    def connect(cls, account, user_id):
        text_to_sign = "Register " + user_id + " for " + str(account.address).lower()
        eth_message = f"{text_to_sign}"
        encoded_message = encode_defunct(text=eth_message)
        signature = account.sign_message(encoded_message)

        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        data = {"signature": signature['signature'].hex(), "message": text_to_sign}
        response = requests.post('http://%s:%d/authenticate/?u=%s' % (cls.host, cls.port, user_id),
                                 data=json.dumps(data), headers=headers)
        return response


if __name__ == '__main__':
    GatewayTester.run()