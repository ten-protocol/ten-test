import secrets
import logging, argparse, sys
from web3 import Web3
from time import perf_counter

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


def run(name, web3, num_iterations):
    logging.info('Client %s started', name)

    times = []
    for i in range(0, num_iterations):
        address = Web3().eth.account.from_key(secrets.token_hex()).address
        start_time = perf_counter()
        chain_id = web3.eth.chain_id
        end_time = perf_counter()
        times.append(end_time - start_time)

    logging.info('Logging times for the RPC request')
    with open('%s.log' % name, 'w') as fp:
        for time in times: fp.write('%d\n' % (time))

    logging.info('Client %s completed', name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='event_listener')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-n', '--client_name', help='The logical name of the client')
    parser.add_argument('-i', '--num_iterations', help='The number of iterations')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    run(args.client_name, web3, int(args.num_iterations))


