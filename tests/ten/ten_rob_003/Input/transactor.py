import logging, random, string, argparse, json, sys, time
from web3 import Web3

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout, level=logging.INFO)


def rand_string():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def create_signed_tx(account, nonce, target, gas_price, gas_limit, chainId):
    build_tx = target.build_transaction(
        {
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas_limit,
            'chainId': chainId
        }
    )
    return account.sign_transaction(build_tx)


def run(id, chainId, web3, account, contract, transactions, gas_limit):
    logging.info('Creating and signing %d transactions', transactions)
    gas_price = web3.eth.gas_price

    txs = []
    for i in range(0, transactions):
        choice = random.randrange(4)
        target = None
        if choice == 0: target = contract.functions.emitSimpleEvent(int(id), rand_string())
        if choice == 1: target = contract.functions.emitArrayEvent(int(id), [1,2], [rand_string(), rand_string()])
        if choice == 2: target = contract.functions.emitStructEvent(int(id), rand_string())
        if choice == 3: target = contract.functions.emitMappingEvent(int(id), [account.address], [random.randrange(100)])
        tx = create_signed_tx(account, i, target, gas_price, gas_limit, chainId)
        txs.append((tx, i))

    logging.info('Bulk sending transactions to the network')
    stats = [0,0]
    receipts = []
    for tx in txs:
        try:
            receipts.append((web3.eth.send_raw_transaction(tx[0].rawTransaction), tx[1]))
            stats[0] += 1
        except Exception as e:
            logging.error('Error sending raw transaction, sent = %d', len(receipts))
            logging.error('Exception is', e)
            stats[1] += 1
    logging.warning('Ratio failures = %.2f', float(stats[1]) / sum(stats))

    logging.info('Waiting for last transaction %s', receipts[-1][0].hex())
    web3.eth.wait_for_transaction_receipt(receipts[-1][0], timeout=900)
    logging.info('Transactor %s completed', id)
    logging.shutdown()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='transactor')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-c', '--chainId', help='The network chain Id')
    parser.add_argument('-p', '--pk', help='The accounts private key')
    parser.add_argument('-a', '--contract_address', help='Address of the contract')
    parser.add_argument('-b', '--contract_abi', help='Abi of the contract')
    parser.add_argument('-i', '--transactions', help='Number of iterations')
    parser.add_argument('-n', '--id', help='The id of the client')
    parser.add_argument('-y', '--gas_limit', help='The gas limit')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    with open(args.contract_abi) as f:
        contract = web3.eth.contract(address=args.contract_address, abi=json.load(f))
    account = web3.eth.account.from_key(args.pk)
    logging.info('Starting transactor %s', args.id)

    run(args.id, int(args.chainId), web3, account, contract, int(args.transactions), int(args.gas_limit))


