from web3 import Web3
import secrets, time, os, json
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


def create_signed_withdrawal(contract, account, nonce, address, value, gas_price, gas_limit, chain_id):
    """Create a signed withdrawal transaction."""
    build_tx = contract.functions.sendNative(address).build_transaction(
        {
            'nonce': nonce,
            'value': value,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': chain_id
        }
    )
    return account.sign_transaction(build_tx)


def run(name, chain_id, web3, account, contract, num_accounts, num_iterations, amount, gas_limit):
    """Run a loop of bulk loading transactions into the mempool, draining, and collating results. """
    accounts = [Web3().eth.account.from_key(x).address for x in [secrets.token_hex() for y in range(0, num_accounts)]]

    logging.info('Creating and signing %d transactions', num_iterations)
    gas_price = web3.eth.gas_price

    txs = []
    scale = 1
    increment = float(2.0 / num_iterations)
    for i in range(0, num_iterations):
        #if i % 3 == 0:
        logging.info('Creating signed withdrawal')
        tx = create_signed_withdrawal(contract, account, i, account.address, amount, int(scale*gas_price), gas_limit, chain_id)
        #else:
        #    tx = create_signed_tx(account, i, random.choice(accounts), amount, int(scale*gas_price), gas_limit, chain_id)
        txs.append((tx, i))
        scale = scale + increment

    logging.info('Bulk sending transactions to the network')
    tx_hashes = []
    for tx in txs:
        try:
            tx_hash = web3.eth.send_raw_transaction(tx[0].rawTransaction)
            tx_hashes.append((tx_hash, tx[1]))
        except Exception as e:
            logging.error('Error sending raw transaction', e)
            logging.warning('Continuing with smaller number of transactions ...')
            break
    logging.info('Number of transactions sent = %d', len(tx_hashes))

    logging.info('Waiting for transactions')
    for entry in tx_hashes:
        try:
            tx_receipt = web3.eth.wait_for_transaction_receipt(entry[0], timeout=30)
            logging.info(tx_receipt)
        except Exception as e:
            logging.error('Timedout waiting for %d' % entry[1])
            logging.error(e)

    logging.info('Logging the timestamps of each transaction')
    with open('%s_throughput.log' % name, 'w') as fp:
        for entry in tx_hashes:
            block_number_deploy = web3.eth.get_transaction(entry[0]).blockNumber
            timestamp = int(web3.eth.get_block(block_number_deploy).timestamp)
            fp.write('%d\n' % timestamp)

    logging.info('Client %s completed', name)
    logging.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='event_listener')
    parser.add_argument('--network_http', help='Connection URL')
    parser.add_argument('--chainId', help='The network chain Id')
    parser.add_argument('--contract_address', help='Address of the contract')
    parser.add_argument('--contract_abi', help='Abi of the contract')
    parser.add_argument('--pk', help='The accounts private key')
    parser.add_argument('--num_accounts', help='Number of accounts to send funds to')
    parser.add_argument('--num_iterations', help='Number of iterations')
    parser.add_argument('--client_name', help='The logical name of the client')
    parser.add_argument('--amount', help='The amount to send in wei')
    parser.add_argument('--gas_limit', help='The gas limit')
    parser.add_argument('--signal_file', help='Poll for this file to initiate sending')
    args = parser.parse_args()

    _web3 = Web3(Web3.HTTPProvider(args.network_http))
    with open(args.contract_abi) as f:
        _contract = _web3.eth.contract(address=args.contract_address, abi=json.load(f))
    _account = _web3.eth.account.from_key(args.pk)
    _name = args.client_name

    logging.info('Starting client %s', _name)
    while not os.path.exists(args.signal_file): time.sleep(0.1)
    logging.info('Signal seen ... running client %s', _name)
    run(_name, int(args.chainId), _web3, _account, _contract, int(args.num_accounts), int(args.num_iterations), int(args.amount), int(args.gas_limit))

