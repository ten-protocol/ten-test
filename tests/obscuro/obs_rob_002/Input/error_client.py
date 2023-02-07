from web3 import Web3
import logging, requests, random
import argparse, json, sys, time
from eth_account.messages import encode_defunct

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


def generate_viewing_key(web3, url, private_key):
    logging.info('Generating viewing key for %s' % private_key)

    account = web3.eth.account.privateKeyToAccount(private_key)

    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    data = {"address": account.address}
    response = requests.post('%s/generateviewingkey/' % url, data=json.dumps(data), headers=headers)

    signed_msg = web3.eth.account.sign_message(encode_defunct(text='vk' + response.text), private_key=private_key)
    data = {"signature": signed_msg.signature.hex(), "address": account.address}
    requests.post('%s/submitviewingkey/' % url, data=json.dumps(data), headers=headers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='event_listener')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-a', '--address', help='Address of the contract')
    parser.add_argument('-b', '--contract_abi', help='Abi of the contract')
    parser.add_argument('-p', '--pk_to_register', help='Private key of account to poll')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    generate_viewing_key(web3, args.network_http, args.pk_to_register)
    with open(args.contract_abi) as f:
        contract = web3.eth.contract(address=args.address, abi=json.load(f))

    logging.info('Client running')
    while True:
        value = random.randint(0, 3)
        try:
            if value == 0:
                contract.functions.force_require().call()
            elif value == 1:
                contract.functions.force_revert().call()
            else:
                contract.functions.force_assert().call()
        except Exception as e:
            logging.info('Exception type: %s' % type(e).__name__)
            logging.info('Exception args: %s' % e.args[0])

        time.sleep(0.1)
