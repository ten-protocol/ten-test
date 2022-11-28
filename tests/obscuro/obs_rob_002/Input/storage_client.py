from web3 import Web3
import logging, requests
import argparse, json, sys
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
    parser.add_argument('-a', '--contract_address', help='Address of the contract')
    parser.add_argument('-b', '--contract_abi', help='Abi of the contract')
    parser.add_argument('-p', '--pk_to_register', help='Private key of account to poll')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    generate_viewing_key(web3, args.network_http, args.pk_to_register)
    with open(args.contract_abi) as f:
        contract = web3.eth.contract(address=args.contract_address, abi=json.load(f))

    logging.info('Client running')
    account = web3.eth.account.privateKeyToAccount(args.pk_to_register)

    logging.info('Building transaction')
    build_tx = contract.functions.store(200).buildTransaction(
        {
            'nonce': web3.eth.get_transaction_count(account.address),
            'gasPrice': 21000,
            'gas': 720000,
            'chainId': web3.eth.chain_id
        }
    )
    logging.info('Signing transaction')
    signed_tx = account.sign_transaction(build_tx)
    logging.info('Sending raw transaction')
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    if tx_receipt.status != 1:
        logging.error('Error performing transaction\n')
    else:
        logging.info('Transaction complete')

