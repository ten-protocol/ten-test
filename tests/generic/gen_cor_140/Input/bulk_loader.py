from web3 import Web3
import secrets, time
import logging, random, argparse, sys

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


def create_signed_tx(account, nonce, address, gas_price, gas_limit, chain_id):
    """Create a signed transaction to transfer funds to an address. """
    tx = {'nonce': nonce,
          'to': address,
          'value': 1,
          'gas': gas_limit,
          'gasPrice': gas_price,
          'chainId': chain_id
          }
    return account.sign_transaction(tx)


def run(start_nonce, web3, account, num_accounts, num_txs):
    """Run a loop of bulk loading transactions into the mempool, draining, and collating results. """
    chain_id = web3.eth.chain_id
    gas_price = web3.eth.gas_price
    tx = {'to': account.address, 'value': 1, 'gasPrice': gas_price}
    gas_limit = web3.eth.estimate_gas(tx)
    accounts = [Web3().eth.account.from_key(x).address for x in [secrets.token_hex() for y in range(0, num_accounts)]]

    logging.info('Creating and signing %d transactions', num_txs)
    signed_txs = []   # (signed tx, nonce) tuple
    for i in range(start_nonce, start_nonce+num_txs):
        tx = create_signed_tx(account, i, random.choice(accounts), gas_price, gas_limit, chain_id)
        signed_txs.append((tx, i))

    logging.info('Bulk sending transactions to the network')
    tx_receipts = []   # (hash, nonce) tuple
    for signed_tx in signed_txs:
        try:
            tx_receipts.append((web3.eth.send_raw_transaction(signed_tx[0].rawTransaction), signed_tx[1]))
        except:
            logging.info('Error sending raw transaction, sent = %d', len(tx_receipts))

    logging.info('Waiting for last transaction')
    web3.eth.wait_for_transaction_receipt(tx_receipts[-1][0], timeout=600)

    logging.info('Iteration completed')
    return tx_receipts[-1][1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='bulk_loader')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-p', '--pk', help='The accounts private key')
    parser.add_argument('-a', '--num_accounts', help='Number of accounts to send funds to')
    parser.add_argument('-i', '--num_transactions', help='Number of transactions to bulk load')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    logging.info('Starting bulk loader')

    nonce = -1
    while True:
        nonce = run(nonce+1, web3, web3.eth.account.from_key(args.pk), int(args.num_accounts), int(args.num_transactions))
        time.sleep(0.1)
