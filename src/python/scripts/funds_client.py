# Utility script for a funded client to transfer funds to a set of recipients. Used when we want to
# create some transactions running in the background for a given test.
#
from web3 import Web3
import logging, requests, random
import argparse, json, sys
from eth_account.messages import encode_defunct

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


def generate_viewing_key(web3, url, private_key):
    logging.info('Generating viewing key for %s', private_key)

    account = web3.eth.account.privateKeyToAccount(private_key)

    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    data = {"address": account.address}
    response = requests.post('%s/generateviewingkey/' % url, data=json.dumps(data), headers=headers)

    signed_msg = web3.eth.account.sign_message(encode_defunct(text='vk' + response.text), private_key=private_key)
    data = {"signature": signed_msg.signature.hex(), "address": account.address}
    requests.post('%s/submitviewingkey/' % url, data=json.dumps(data), headers=headers)


def transfer_value(web3, account, amount, recipient):
    tx = {
        'nonce': web3.eth.get_transaction_count(account.address),
        'to': recipient,
        'value': web3.toWei(amount, 'ether'),
        'gas': 4 * 720000,
        'gasPrice': web3.eth.gas_price
    }
    signed_tx = account.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    if tx_receipt.status != 1:
        logging.error('Error performing transaction')
    else:
        logging.info('Transaction complete ... transferred %d to %s', amount, recipient)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='funds_client')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-p', '--pk_to_register', help='Private key of account to poll')
    parser.add_argument('-r', '--recipients', help='Comma separated list of recipient pks')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    generate_viewing_key(web3, args.network_http, args.pk_to_register)
    account = web3.eth.account.privateKeyToAccount(args.pk_to_register)
    recipients = args.recipients.split(',')

    logging.info('Client running')
    while True:
        balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
        logging.info('Account balance is %.9f', balance)
        transfer_value(web3, account, 0.0001, random.choice(recipients))

