from web3 import Web3
import logging
import argparse, json, sys

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout, level=logging.INFO)


def create_signed_tx(name, account, nonce, contract, gas_price, gas_limit, chainId):
    build_tx = contract.functions.setItem(name, nonce).build_transaction(
        {
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas_limit,
            'chainId': chainId
        }
    )
    return account.sign_transaction(build_tx)


def tenths(list):
    every_tenth = list[9::10]
    last_element = list[-1]
    if last_element not in every_tenth:
        return every_tenth + [last_element]
    return every_tenth


def run(name, chainId, web3, account, contract, num_iterations, gas_limit):
    """Run a loop of bulk loading transactions into the mempool, draining, and collating results. """
    logging.info('Creating and signing %d transactions', num_iterations)
    gas_price = web3.eth.gas_price

    signed_txs = []
    for i in range(0, num_iterations):
        signed_tx = create_signed_tx(name, account, i, contract, gas_price, gas_limit, chainId)
        signed_txs.append((signed_tx, i))

    logging.info('Bulk sending transactions to the network')
    tx_hashes = []
    for tx in signed_txs:
        try:
            tx_hashes.append((web3.eth.send_raw_transaction(tx[0].rawTransaction), tx[1]))
        except Exception as e:
            logging.error('Error sending raw transaction', e)
            logging.warning('Continuing with smaller number of transactions ...')
            break
    logging.info('Number of transactions sent = %d', len(tx_hashes))

    for tx_hash in tenths(tx_hashes):
        logging.info('Waiting for transaction receipt number  %s', tx_hash[1])
        web3.eth.wait_for_transaction_receipt(tx_hash[0], timeout=900)
    logging.info('Retrieved value for %s is %d', name, contract.functions.getItem(name).call())

    logging.info('Constructing binned data from the transaction receipts')
    with open('%s.log' % name, 'w') as fp:
        for tx_hash in tx_hashes:
            block_number = web3.eth.get_transaction(tx_hash[0]).blockNumber
            timestamp = int(web3.eth.get_block(block_number).timestamp)
            fp.write('%d %d %d\n' % (tx_hash[1], timestamp, block_number))

    logging.info('Client %s completed', name)
    logging.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='storage_client')
    parser.add_argument('--network_http', help='Connection URL')
    parser.add_argument('--chainId', help='The network chain Id')
    parser.add_argument('--pk', help='The accounts private key')
    parser.add_argument('--contract_address', help='Address of the contract')
    parser.add_argument('--contract_abi', help='Abi of the contract')
    parser.add_argument('--num_iterations', help='Number of iterations')
    parser.add_argument('--client_name', help='The logical name of the client')
    parser.add_argument('--gas_limit', help='The gas limit')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    with open(args.contract_abi) as f:
        contract = web3.eth.contract(address=args.contract_address, abi=json.load(f))
    account = web3.eth.account.from_key(args.pk)
    logging.info('Starting client %s', args.client_name)

    run(args.client_name, int(args.chainId), web3, account, contract, int(args.num_iterations), int(args.gas_limit))


