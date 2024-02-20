import logging, argparse, sys, time
from web3 import Web3

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


def run(name, web3, num_iterations):
    logging.info('Client %s started', name)
    address = Web3().eth.account.from_key(args.pk).address

    data = []
    for i in range(0, num_iterations):
        start_time = time.perf_counter_ns()
        balance = web3.eth.get_balance(address)
        end_time = time.perf_counter_ns()
        logging.info('%d %d %d', start_time, end_time, balance)
        data.append((end_time - start_time)/1e6)

    logging.info('Logging times for the RPC request')
    with open('%s.log' % name, 'w') as fp:
        for d in data: fp.write('%d\n' % d)

    logging.info('Client %s completed', name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='event_listener')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-n', '--client_name', help='The logical name of the client')
    parser.add_argument('-i', '--num_iterations', help='The number of iterations')
    parser.add_argument('-p', '--pk', help='Private key used to request balance')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    run(args.client_name, web3, int(args.num_iterations))


