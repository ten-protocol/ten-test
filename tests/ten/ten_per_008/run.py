import os, random, string, time
from datetime import datetime
from pysys.constants import FOREGROUND
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper
from ten.test.contracts.emitter import TransparentEventEmitter


class PySysTest(TenNetworkTest):
    NUM_TRANSACTIONS = 250  # number of txs the transactors will perform

    def execute(self):
        # connect to network on the primary gateway and deploy contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        emitter = TransparentEventEmitter(self, web3, 100)
        emitter.deploy(network, account)

        # estimate how much gas each transactor will need
        rstr = self.rand_str()
        chain_id = network.chain_id()
        gas_price = web3.eth.gas_price
        params = {'from': account.address, 'chainId': chain_id, 'gasPrice': gas_price}
        limits = [emitter.contract.functions.emitSimpleEvent(1, rstr).estimate_gas(params)]
        limits.append(emitter.contract.functions.emitArrayEvent(1, [1, 2], [rstr, rstr]).estimate_gas(params))
        limits.append(emitter.contract.functions.emitStructEvent(1, rstr).estimate_gas(params))
        limits.append(emitter.contract.functions.emitMappingEvent(1, [account.address], [200]).estimate_gas(params))
        gas_limit = max(limits)
        funds_needed = 1.1 * self.NUM_TRANSACTIONS * (gas_price * gas_limit)

        results_file = os.path.join(self.output, 'results.log')
        throughputs = []
        with open(results_file, 'w') as fp:
            for clients in (2,4,6):
                self.log.info('')
                self.log.info('Running for %d clients' % clients)
                out_dir = os.path.join(self.output, 'clients_%d' % clients)
                os.mkdir(out_dir)
                txs_sent, duration, throughput = self.do_run(clients, funds_needed, emitter, gas_limit, out_dir)
                self.log.info('Stats for run: ')
                self.log.info('  Time to perform run:   %d', duration)
                self.log.info('  Num transactions sent: %d', txs_sent)
                self.log.info('  Bulk rate throughput %.2f (transactions/sec)' % throughput)
                fp.write('%d %.2f\n' % (clients, throughput))
                throughputs.append(throughput)

        branch = GnuplotHelper.buildInfo().branch
        average = float(sum(throughputs)) / float(len(throughputs))
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'),
                            branch, date,
                            str(self.mode), '%.3f' % average)

    def do_run(self, num_clients, funds_needed, emitter, gas_limit, out_dir):
        # set up the transactors and run the subscribers
        clients = []
        subscribers = []
        for id in range(0, num_clients):
            pk, account, network = self.setup_transactor(funds_needed)
            clients.append((id, pk, account, network))
            process = self.run_subscriber(network, emitter, account, id, out_dir)
            subscribers.append(process)

        # run the transactors serially in the foreground
        txs_sent = 0
        start_ns = time.perf_counter_ns()
        for id, pk, account, network in clients:
            self.run_transactor(id, emitter, pk, network, gas_limit, out_dir)
            self.ratio_failures(file=os.path.join(out_dir, 'transactor%d.out' % id))
            txs_sent += self.txs_sent(file=os.path.join(out_dir, 'transactor%d.out' % id))
        end_ns = time.perf_counter_ns()
        bulk_throughput = float(txs_sent) / float((end_ns - start_ns) / 1e9)

        # stop the subscribers
        for subscriber in subscribers: subscriber.stop()

        return txs_sent, int((end_ns - start_ns) / 1e9), bulk_throughput

    def setup_transactor(self, funds_needed):
        pk = self.get_ephemeral_pk()
        network = self.get_network_connection()
        web3, account = network.connect(self, private_key=pk, check_funds=False)
        self.distribute_native(account, web3.from_wei(funds_needed, 'ether'))
        return pk, account, network

    def run_transactor(self, id, emitter, pk, network, gas_limit, out_dir):
        stdout = os.path.join(out_dir, 'transactor%s.out' % id)
        stderr = os.path.join(out_dir, 'transactor%s.err' % id)
        script = os.path.join(self.input, 'transactor.py')
        args = []
        args.extend(['--network_http', network.connection_url()])
        args.extend(['--chainId', '%s' % network.chain_id()])
        args.extend(['--pk', pk])
        args.extend(['--contract_address', '%s' % emitter.address])
        args.extend(['--contract_abi', '%s' % emitter.abi_path])
        args.extend(['--transactions', '%d' % self.NUM_TRANSACTIONS])
        args.extend(['--id', '%d' % id])
        args.extend(['--gas_limit', '%d' % gas_limit])
        self.run_python(script, stdout, stderr, args, state=FOREGROUND, timeout=300)

    def run_subscriber(self, network, emitter, account, id_filter, out_dir):
        stdout = os.path.join(out_dir, 'subscriber%d.out' % id_filter)
        stderr = os.path.join(out_dir, 'subscriber%d.err' % id_filter)
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--contract_address', '%s' % emitter.address])
        args.extend(['--contract_abi', '%s' % emitter.abi_path])
        args.extend(['--id_filter', str(id_filter)])
        args.extend(['--address_filter', account.address])
        pHandle = self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Listening for filtered events...', timeout=10)
        return pHandle

    def rand_str(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
