from web3 import Web3
import secrets, time
import logging, random, argparse, sys

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout, level=logging.INFO)

nonces = {}
counts = {}


def create_signed_tx(account, address, value, gas_price, gas_limit, chain_id):
    """Create a signed transaction to transfer funds to an address. """
    if account.address in nonces: nonce = nonces[account.address] + 1
    else: nonce = 0
    nonces[account.address] = nonce

    tx = {'nonce': nonce,
          'from': account.address,
          'to': address,
          'value': value,
          'gas': gas_limit,
          'gasPrice': gas_price,
          'chainId': chain_id
          }
    return account.sign_transaction(tx)


def run(name, chainId, web3, sending_accounts, num_accounts, num_iterations, amount, gas_limit):
    """Run a loop of bulk loading transactions into the mempool, draining, and collating results. """
    accounts = []
    for i in range(0, num_accounts):
        accounts.append(Web3().eth.account.from_key(secrets.token_hex(32)).address)

    logging.info('Creating and signing %d transactions', num_iterations)
    gas_price = web3.eth.gas_price
    signed_txs = []
    for i in range(0, num_iterations):
        signed_tx = create_signed_tx(random.choice(sending_accounts), random.choice(accounts), amount, gas_price, gas_limit, chainId)
        signed_txs.append((signed_tx, i))

    logging.info('Bulk sending transactions to the network')
    tx_hashes = []
    start_time = time.perf_counter()
    for signed_tx in signed_txs:
        try:
            tx_hashes.append((web3.eth.send_raw_transaction(signed_tx[0].rawTransaction), signed_tx[1]))
        except Exception as e:
            logging.error('Error sending raw transaction', e)
            logging.warning('Continuing with smaller number of transactions ...')
            break
    logging.info('Number of transactions sent = %d', len(tx_hashes))

    end_time = time.perf_counter()
    duration = end_time - start_time
    logging.info('Time to send all transactions was %.4f', duration)

    logging.info('Waiting for last transaction')
    start_time = time.perf_counter()
    web3.eth.wait_for_transaction_receipt(tx_hashes[-1][0], timeout=600)
    end_time = time.perf_counter()
    logging.info('Time to wait for last transaction was %.4f', (end_time - start_time))

    logging.info('Requesting all transaction receipts')
    times = []
    with open('%s.log' % name, 'w') as fp:
        for tx_hash in tx_hashes:
            start_time = time.perf_counter()
            web3.eth.wait_for_transaction_receipt(tx_hash[0], timeout=30)
            end_time = time.perf_counter()
            times.append((end_time - start_time))
            block_number_deploy = web3.eth.get_transaction(tx_hash[0]).blockNumber
            timestamp = int(web3.eth.get_block(block_number_deploy).timestamp)
            fp.write('%d %d %d %.4f\n' % (tx_hash[1], block_number_deploy, timestamp, (end_time - start_time)))
    logging.info('Average time to wait for transaction receipt was %.4f', (sum(times) / float(len(times))))

    for account in nonces.keys():
        balance = web3.eth.get_balance(account)
        logging.info('Account %s has nonce %d, balance %d', account, nonces[account], balance)
    logging.info('Client %s completed', name)
    logging.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='event_listener')
    parser.add_argument('--network_http', help='Connection URL')
    parser.add_argument('--chainId', help='The network chain Id')
    parser.add_argument('--pk_file', help='A file containing a list of PKs to use')
    parser.add_argument('--num_accounts', help='Number of accounts to send funds to')
    parser.add_argument('--num_iterations', help='Number of iterations')
    parser.add_argument('--client_name', help='The logical name of the client')
    parser.add_argument('--amount', help='The amount to send in wei')
    parser.add_argument('--gas_limit', help='The gas limit')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    logging.info('Starting client %s', args.client_name)

    sending_accounts = []
    with open(args.pk_file, 'r') as fp:
        for line in fp.readlines():
            sending_accounts.append(web3.eth.account.from_key(line.strip()))

    run(args.client_name, int(args.chainId), web3, sending_accounts, int(args.num_accounts), int(args.num_iterations),
        int(args.amount), int(args.gas_limit))
