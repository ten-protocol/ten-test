from web3 import Web3
import logging
import argparse, json, sys

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


def create_signed_tx(name, account, nonce, contract, gas_price, chainId):
    build_tx = contract.functions.setItem(name, nonce).buildTransaction(
        {
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': 720000,
            'chainId': chainId
        }
    )
    return account.sign_transaction(build_tx)


def run(name, chainId, web3, account, contract, num_iterations):
    """Run a loop of bulk loading transactions into the mempool, draining, and collating results. """
    logging.info('Creating and signing %d transactions', num_iterations)
    gas_price = web3.eth.gas_price

    txs = []
    for i in range(0, num_iterations):
        tx = create_signed_tx(name, account, i, contract, gas_price, chainId)
        txs.append((tx, i))

    logging.info('Bulk sending transactions to the network')
    receipts = []
    for tx in txs:
        try:
            receipts.append((web3.eth.send_raw_transaction(tx[0].rawTransaction), tx[1]))
        except Exception as e:
            logging.info('Error sending raw transaction, sent = %d', len(receipts))
            logging.info('Exception is', e)

    logging.info('Waiting for last transaction %s', receipts[-1][0].hex())
    web3.eth.wait_for_transaction_receipt(receipts[-1][0], timeout=900)
    logging.info('Retrieved value for %s is %d', name, contract.functions.getItem(name).call())

    logging.info('Constructing binned data from the transaction receipts')
    with open('%s.log' % name, 'w') as fp:
        for receipt in receipts:
            block_number_deploy = web3.eth.get_transaction(receipt[0]).blockNumber
            timestamp = int(web3.eth.get_block(block_number_deploy).timestamp)
            fp.write('%d %d\n' % (receipt[1], timestamp))

    logging.info('Client %s completed', name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='storage_client')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-c', '--chainId', help='The network chain Id')
    parser.add_argument('-p', '--pk', help='The accounts private key')
    parser.add_argument('-a', '--contract_address', help='Address of the contract')
    parser.add_argument('-b', '--contract_abi', help='Abi of the contract')
    parser.add_argument('-i', '--num_iterations', help='Number of iterations')
    parser.add_argument('-n', '--client_name', help='The logical name of the client')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    with open(args.contract_abi) as f:
        contract = web3.eth.contract(address=args.contract_address, abi=json.load(f))
    account = web3.eth.account.from_key(args.pk)
    logging.info('Starting client %s', args.client_name)

    run(args.client_name, int(args.chainId), web3, account, contract, int(args.num_iterations))


