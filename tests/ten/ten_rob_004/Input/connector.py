import logging, requests, time
import os, secrets, argparse, json, sys
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_structured_data

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


def join(host, port):
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.get('%s:%d/v1/join/' % (host, port),  headers=headers)
    return response.text


def register(chainId, account, host, port, user_id):
    domain = {'name': 'Ten', 'version': '1.0', 'chainId': chainId}
    message = {'EncryptionToken': "0x"+user_id}
    types = {
        'EIP712Domain': [
            {'name': 'name', 'type': 'string'},
            {'name': 'version', 'type': 'string'},
            {'name': 'chainId', 'type': 'uint256'},
        ],
        'Authentication': [
            {'name': 'EncryptionToken', 'type': 'address'},
        ],
    }
    typed_data = {'types': types, 'domain': domain, 'primaryType': 'Authentication',  'message': message}

    signable_msg_from_dict = encode_structured_data(typed_data)
    signed_msg_from_dict = Account.sign_message(signable_msg_from_dict, account.key)

    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    data = {"signature": signed_msg_from_dict.signature.hex(), "address": account.address}
    return requests.post('%s:%d/v1/authenticate/?u=%s' % (host, port, user_id),
                         data=json.dumps(data), headers=headers)


def wait(file, timeout=20):
    start = time.time()
    while True:
        if time.time() > start + timeout:
            logging.error('Timed out waiting for the trigger file')
            break
        time.sleep(0.01)
        if os.path.exists(file): return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='error_client')
    parser.add_argument('-t', '--host', help='Connection host')
    parser.add_argument('-p', '--port', help='Connection port')
    parser.add_argument('-a', '--pk', help='Account private key')
    parser.add_argument('-b', '--balance', help='Expected balance')
    parser.add_argument('-f', '--trigger', help='Path to the trigger file')
    parser.add_argument('-n', '--iterations', help='Number of iterations to perform')
    parser.add_argument('-x', '--additional_accounts', help='Additional accounts to register each iteration')
    parser.add_argument('-c', '--chain_id', help='The network chain ID')
    args = parser.parse_args()

    account = Web3().eth.account.privateKeyToAccount(args.pk)
    logging.info('Client running ... waiting for trigger file')
    wait(args.trigger)
    logging.info('Client starting ... trigger file seen')

    for i in range(0, int(args.iterations)):
        logging.info('Joining network using url %s:%s/v1/join/', args.host, args.port)
        user_id = join(args.host, int(args.port))

        logging.info('Registering account %s with the network on user id %s', account.address, user_id)
        response = register(int(args.chain_id), account, args.host, int(args.port), user_id)
        logging.info('Registration success was %s', response.ok)
        web3 = Web3(Web3.HTTPProvider('%s:%s/v1/?u=%s' % (args.host, args.port, user_id)))

        for j in range(0, int(args.additional_accounts)):
            _account = Web3().eth.account.privateKeyToAccount(secrets.token_hex(32))
            response = register(int(args.chain_id), _account, args.host, int(args.port), user_id)
            logging.info('Additional clients, registration for %s success was %s', _account.address, response.ok)

        balance = web3.eth.get_balance(account.address)
        logging.info('Balance is %d', balance)
        time.sleep(0.01)

    logging.info('Client completed')
