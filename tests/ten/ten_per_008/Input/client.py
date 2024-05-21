import logging, argparse, sys, time, os
from web3 import Web3

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout, level=logging.INFO)


def run(name, web3, num_iterations, start):
    address = Web3().eth.account.from_key(args.pk).address

    latency = []
    num_requests = 0
    throughput = []
    for i in range(0, num_iterations):
        try:
            start_time = time.perf_counter_ns()
            web3.eth.get_balance(address)
            end_time = time.perf_counter_ns()
            latency.append((end_time - start_time)/1e6)
            num_requests = num_requests + 1
            throughput.append(((end_time - start)/1e9, num_requests))
        except Exception as e:
            logging.error('Error performing transaction %s', e)

    logging.info('Logging latency for the RPC requests')
    with open('%s_latency.log' % name, 'w') as fp:
        for l in latency: fp.write('%d\n' % l)

    logging.info('Logging throughput for the RPC requests')
    with open('%s_throughput.log' % name, 'w') as fp:
        for t,n in throughput: fp.write('%.3f %d\n' % (t,n))

    logging.info('Client %s completed', name)
    logging.shutdown()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='event_listener')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-n', '--client_name', help='The logical name of the client')
    parser.add_argument('-i', '--num_iterations', help='The number of iterations')
    parser.add_argument('-p', '--pk', help='Private key used to request balance')
    parser.add_argument('-s', '--start', help='Starting time')
    parser.add_argument('-f', '--signal_file', help='Poll for this file to initiate sending')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    logging.info('Starting client %s', args.client_name)
    while not os.path.exists(args.signal_file): time.sleep(0.1)
    run(args.client_name, web3, int(args.num_iterations), int(args.start))


