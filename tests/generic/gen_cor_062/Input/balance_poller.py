from web3 import Web3
import requests, logging, time
import argparse, json, sys
from eth_account.messages import encode_defunct

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


def generate_viewing_key(web3, url, address, private_key):
    logging.info('Generating viewing key for %s' % private_key)

    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    data = {"address": address}
    response = requests.post('%s/generateviewingkey/' % url, data=json.dumps(data), headers=headers)

    signed_msg = web3.eth.account.sign_message(encode_defunct(text='vk' + response.text), private_key=private_key)
    data = {"signature": signed_msg.signature.hex(), "address": address}
    requests.post('%s/submitviewingkey/' % url, data=json.dumps(data), headers=headers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='balance_poller')
    parser.add_argument('-u', '--url', help='Connection URL')
    parser.add_argument('-a', '--address', help='Address of the contract')
    parser.add_argument('-b', '--abi', help='Abi of the contract')
    parser.add_argument('-p', '--pk', help='Private key of account to poll')
    parser.add_argument("--obscuro", action='store_true', help='True if running against obscuro')
    args = parser.parse_args()

    logging.info('URL: %s' % args.url)
    logging.info('ADR: %s' % args.address)
    logging.info('ABI: %s' % args.abi)
    logging.info('PK: %s' % args.pk)

    web3 = Web3(Web3.HTTPProvider(args.url))
    account = web3.eth.account.privateKeyToAccount(args.pk)
    if args.obscuro: generate_viewing_key(web3, args.url, account.address, args.pk)
    with open(args.abi) as f:
        contract = web3.eth.contract(address=args.address, abi=json.load(f))

    logging.info('Starting to run the polling loop')
    last_balance = 0
    while True:
        balance = contract.functions.balanceOf(account.address).call()
        if balance > last_balance:
            last_balance = balance
            logging.info('New balance = %s' % balance)
        time.sleep(2)
