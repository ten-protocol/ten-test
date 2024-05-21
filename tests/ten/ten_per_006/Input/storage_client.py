from web3 import Web3
import logging, random
import argparse, json, sys, time

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout, level=logging.INFO)


def timeit(function):
    """Decorator function to time a method call and return the time. """
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        function(*args, **kwargs)
        end_time = time.perf_counter()
        return end_time - start_time

    return wrapper


@timeit
def store_value(value, web3, account, contract, gas_limit):
    build_tx = contract.functions.store(value).build_transaction(
        {
            'nonce': web3.eth.get_transaction_count(account.address),
            'gasPrice': web3.eth.gas_price,
            'gas': gas_limit,
            'chainId': web3.eth.chain_id
        }
    )
    signed_tx = account.sign_transaction(build_tx)
    stats = [0,0]
    try:
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        if tx_receipt.status != 1:
            logging.error('Error performing transaction\n')
            stats[1] += 1
        else:
            logging.info('Transaction complete - stored value %d', value)
            stats[0] += 1
    except Exception as e:
        logging.error('Error performing transaction %s', e)
        stats[1] += 1

    logging.warning('Ratio transaction failures = %.2f', float(stats[1]) / sum(stats))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='storage_client')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-a', '--address', help='Address of the contract')
    parser.add_argument('-b', '--contract_abi', help='Abi of the contract')
    parser.add_argument('-i', '--num_iterations', help='Number of iterations')
    parser.add_argument('-p', '--pk_to_register', help='Private key of account')
    parser.add_argument('-f', '--output_file', help='File to log the results to')
    parser.add_argument('-y', '--gas_limit', help='The gas limit to use')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    with open(args.contract_abi) as f:
        contract = web3.eth.contract(address=args.address, abi=json.load(f))

    logging.info('Client running')
    account = web3.eth.account.from_key(args.pk_to_register)

    with open(args.output_file, 'w') as fp:
        for i in range(0, int(args.num_iterations)):
            fp.write('%.4f\n' % store_value(random.randint(0,100), web3, account, contract, int(args.gas_limit)))
            fp.flush()
    logging.info('Client completed')
    logging.shutdown()


