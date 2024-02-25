import logging, argparse, sys, time
from web3 import Web3

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


def run(name, web3, num_iterations):
    logging.info('Client %s started', name)
    address = Web3().eth.account.from_key(args.pk).address

    latency = []
    num_requests = 0
    throughput = []
    start = time.perf_counter_ns()
    for i in range(0, num_iterations):
        start_time = time.perf_counter_ns()
        balance = web3.eth.get_balance(address)
        end_time = time.perf_counter_ns()
        logging.info('%d %d %d', start_time, end_time, balance)
        latency.append((end_time - start_time)/1e6)
        num_requests = num_requests + 1
        throughput.append(((end_time - start)/1e9, num_requests))

    logging.info('Logging latency for the RPC requests')
    with open('%s_latency.log' % name, 'w') as fp:
        for l in latency: fp.write('%d\n' % l)

    logging.info('Logging throughput for the RPC requests')
    with open('%s_throughput.log' % name, 'w') as fp:
        for t,n in throughput: fp.write('%.3f %d\n' % (t,n))

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


