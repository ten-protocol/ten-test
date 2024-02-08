# Utility script for a funded client to transfer funds to a set of recipients. Used when we want to
# create some transactions running in the background for a given test. Note that it is assumed the
# client / account has been registered outside the scope of this script (e.g. for use against Ten)
#
from web3 import Web3
import logging, random
import argparse, sys

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


def transfer_value(web3, account, gas_estimate, recipient):
    tx = {
        'nonce': web3.eth.get_transaction_count(account.address),
        'to': recipient,
        'value': 1,
        'gas': gas_estimate,
        'gasPrice': web3.eth.gas_price
    }
    signed_tx = account.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    if tx_receipt.status != 1:
        logging.error('Error performing transaction')
    else:
        logging.info('Transaction complete ... transferred 1 wei to %s', recipient)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='funds_client')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-p', '--pk_to_register', help='Private key of account to poll')
    parser.add_argument('-r', '--recipients', help='Comma separated list of recipient pks')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    account = web3.eth.account.from_key(args.pk_to_register)
    recipients = args.recipients.split(',')

    logging.info('Client running')

    gas_price = web3.eth.gas_price
    tx = {'to': random.choice(recipients), 'value': 1, 'gasPrice': gas_price}
    gas_estimate = web3.eth.estimate_gas(tx)
    logging.info('Gas estimate is %d', gas_estimate)

    while True:
        balance = web3.eth.get_balance(account.address)
        logging.info('Account balance is %d', balance)
        transfer_value(web3, account, gas_estimate, random.choice(recipients))



