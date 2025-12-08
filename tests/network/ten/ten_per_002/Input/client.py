from web3 import Web3
import secrets
import logging, random, argparse, sys

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout, level=logging.INFO)


def create_signed_tx(account, nonce, address, value, gas_price, gas_limit, chain_id):
    """Create a signed transaction to transfer funds to an address. """
    tx = {'nonce': nonce,
          'to': address,
          'value': value,
          'gas': gas_limit,
          'gasPrice': gas_price,
          'chainId': chain_id
          }
    return account.sign_transaction(tx)


def run(name, chainId, web3, account, num_accounts, num_iterations, amount, gas_limit):
    """Run a loop of bulk loading transactions into the mempool, draining, and collating results. """
    accounts = [Web3().eth.account.from_key(x).address for x in [secrets.token_hex() for y in range(0, num_accounts)]]

    logging.info('Creating and signing %d transactions', num_iterations)
    gas_price = web3.eth.gas_price

    signed_txs = []
    for i in range(0, num_iterations):
        signed_tx = create_signed_tx(account, i, random.choice(accounts), amount, gas_price, gas_limit, chainId)
        signed_txs.append((signed_tx, i))

    logging.info('Bulk sending transactions to the network')
    tx_hashes = []
    for signed_tx in signed_txs:
        try:
            tx_hashes.append((web3.eth.send_raw_transaction(signed_tx[0].rawTransaction), signed_tx[1]))
        except Exception as e:
            logging.error('Error sending raw transaction', e)
            logging.warning('Continuing with smaller number of transactions ...')
            break
    logging.info('Number of transactions sent = %d', len(tx_hashes))

    logging.info('Waiting for last transaction')
    web3.eth.wait_for_transaction_receipt(tx_hashes[-1][0], timeout=600)

    logging.info('Constructing binned data from the transaction receipts')
    with open('%s.log' % name, 'w') as fp:
        for tx_hash in tx_hashes:
            block_number_deploy = web3.eth.get_transaction(tx_hash[0]).blockNumber
            timestamp = int(web3.eth.get_block(block_number_deploy).timestamp)
            fp.write('%d %d\n' % (tx_hash[1], timestamp))

    logging.info('Client %s completed', name)
    logging.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='event_listener')
    parser.add_argument('--network_http', help='Connection URL')
    parser.add_argument('--chainId', help='The network chain Id')
    parser.add_argument('--pk', help='The accounts private key')
    parser.add_argument('--num_accounts', help='Number of accounts to send funds to')
    parser.add_argument('--num_iterations', help='Number of iterations')
    parser.add_argument('--client_name', help='The logical name of the client')
    parser.add_argument('--amount', help='The amount to send in wei')
    parser.add_argument('--gas_limit', help='The gas limit')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    account = web3.eth.account.from_key(args.pk)
    name = args.client_name
    logging.info('Starting client %s', name)

    run(name, int(args.chainId), web3, account, int(args.num_accounts), int(args.num_iterations), int(args.amount), int(args.gas_limit))

