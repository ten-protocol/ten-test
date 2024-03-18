from web3 import Web3
import secrets, time, os
import logging, random, argparse, sys

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


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

    txs = []
    scale = 1
    increment = float(2.0 / num_iterations)
    for i in range(0, num_iterations):
        tx = create_signed_tx(account, i, random.choice(accounts), amount, int(scale*gas_price), gas_limit, chainId)
        txs.append((tx, i))
        scale = scale + increment

    logging.info('Bulk sending transactions to the network')
    receipts = []
    for tx in txs:
        try:
            receipt = web3.eth.send_raw_transaction(tx[0].rawTransaction)
            receipts.append((receipt, tx[1]))
        except:
            logging.info('Error sending raw transaction, sent = %d', len(receipts))

    logging.info('Waiting for last transaction')
    web3.eth.wait_for_transaction_receipt(receipts[-1][0], timeout=600)

    logging.info('Logging the timestamps of each transaction')
    with open('%s_throughput.log' % name, 'w') as fp:
        for receipt in receipts:
            block_number_deploy = web3.eth.get_transaction(receipt[0]).blockNumber
            timestamp = int(web3.eth.get_block(block_number_deploy).timestamp)
            fp.write('%d\n' % timestamp)

    logging.info('Client %s completed', name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='event_listener')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-c', '--chainId', help='The network chain Id')
    parser.add_argument('-p', '--pk', help='The accounts private key')
    parser.add_argument('-a', '--num_accounts', help='Number of accounts to send funds to')
    parser.add_argument('-i', '--num_iterations', help='Number of iterations')
    parser.add_argument('-n', '--client_name', help='The logical name of the client')
    parser.add_argument('-x', '--amount', help='The amount to send in wei')
    parser.add_argument('-y', '--gas_limit', help='The gas limit')
    parser.add_argument('-s', '--signal_file', help='Poll for this file to initiate sending')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    account = web3.eth.account.from_key(args.pk)
    name = args.client_name

    logging.info('Starting client %s', name)
    #while not os.path.exists(args.signal_file): time.sleep(0.1)
    logging.info('Signal seen ... running client %s', name)
    run(name, int(args.chainId), web3, account, int(args.num_accounts), int(args.num_iterations), int(args.amount), int(args.gas_limit))

