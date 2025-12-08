from web3 import Web3
import secrets, time, os, json
import logging, random, argparse, sys

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout, level=logging.INFO)


def create_signed_withdrawal(contract, account, nonce, address, value, gas_price, withdraw_gas, chain_id, fees):
    """Create a signed withdrawal transaction."""
    target = contract.functions.sendNative(address)
    params = {
        'nonce': nonce,
        'value': value+fees,
        'gas': withdraw_gas,
        'gasPrice': gas_price,
        'chainId': chain_id
    }
    build_tx = target.build_transaction(params)
    return account.sign_transaction(build_tx)


def create_signed_tx(account, nonce, address, value, gas_price, transfer_gas, chain_id):
    """Create a signed transaction to transfer funds to an address. """
    tx = {'nonce': nonce,
          'to': address,
          'value': value,
          'gas': transfer_gas,
          'gasPrice': gas_price,
          'chainId': chain_id
          }
    return account.sign_transaction(tx)


def tenths(list):
    every_tenth = list[9::10]
    last_element = list[-1]
    if last_element not in every_tenth:
        return every_tenth + [last_element]
    return every_tenth


def run(name, chain_id, web3, account, contract, num_accounts, num_iterations, amount, transfer_gas, withdraw_gas, fees):
    """Run a loop of bulk loading transactions into the mempool, draining, and collating results. """
    accounts = [Web3().eth.account.from_key(x).address for x in [secrets.token_hex() for y in range(0, num_accounts)]]

    logging.info('Creating and signing %d transactions', num_iterations)
    gas_price = web3.eth.gas_price

    signed_txs = []
    scale = 1
    withdrawals = 0
    increment = float(2.0 / num_iterations)
    for i in range(0, num_iterations):
        if (i % 16) == 0:
            withdrawals = withdrawals + 1
            signed_tx = create_signed_withdrawal(contract, account, i, account.address, amount, int(scale*gas_price), withdraw_gas, chain_id, fees)
        else:
            signed_tx = create_signed_tx(account, i, random.choice(accounts), amount, int(scale*gas_price), transfer_gas, chain_id)
        signed_txs.append((signed_tx, i))
        scale = scale + increment

    logging.info('Bulk sending transactions to the network')
    tx_hashes = []
    for signed_tx in signed_txs:
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx[0].rawTransaction)
            tx_hashes.append((tx_hash, signed_tx[1]))
        except Exception as e:
            logging.error('Error sending raw transaction', e)
            logging.warning('Continuing with smaller number of transactions ...')
            break
    logging.info('Number of transactions sent = %d', len(tx_hashes))
    logging.info('Number of withdrawals were  = %d', withdrawals)

    logging.info('Waiting for transactions')
    for tx_hash in tenths(tx_hashes):
        try:
            web3.eth.wait_for_transaction_receipt(tx_hash[0], timeout=900)
        except Exception as e:
            logging.error('Timed out waiting for %d' % tx_hash[1])
            logging.error(e)

    logging.info('Logging the timestamps of each transaction')
    with open('%s_throughput.log' % name, 'w') as fp:
        for tx_hash in tx_hashes:
            block_number_deploy = web3.eth.get_transaction(tx_hash[0]).blockNumber
            timestamp = int(web3.eth.get_block(block_number_deploy).timestamp)
            fp.write('%d\n' % timestamp)

    logging.info('Client %s completed', name)
    logging.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='event_listener')
    parser.add_argument('--network_http', help='Connection URL')
    parser.add_argument('--chainId', help='The network chain Id')
    parser.add_argument('--bridge_address', help='Address of the contract')
    parser.add_argument('--bridge_abi', help='Abi of the contract')
    parser.add_argument('--bridge_fees', help='Bridge fees')
    parser.add_argument('--pk', help='The accounts private key')
    parser.add_argument('--num_accounts', help='Number of accounts to send funds to')
    parser.add_argument('--num_iterations', help='Number of iterations')
    parser.add_argument('--client_name', help='The logical name of the client')
    parser.add_argument('--amount', help='The amount to send in wei')
    parser.add_argument('--transfer_gas', help='The gas limit for transfers')
    parser.add_argument('--withdraw_gas', help='The gas limit for withdrawals')
    parser.add_argument('--signal_file', help='Poll for this file to initiate sending')
    args = parser.parse_args()

    web3: Web3 = Web3(Web3.HTTPProvider(args.network_http))
    with open(args.bridge_abi) as f:
        contract = web3.eth.contract(address=args.bridge_address, abi=json.load(f))
    account = web3.eth.account.from_key(args.pk)
    name = args.client_name

    logging.info('Starting client %s', name)
    while not os.path.exists(args.signal_file): time.sleep(0.1)
    logging.info('Signal seen ... running client %s', name)
    run(name, int(args.chainId), web3, account, contract, int(args.num_accounts), int(args.num_iterations),
        int(args.amount), int(args.transfer_gas), int(args.withdraw_gas), int(args.bridge_fees))
