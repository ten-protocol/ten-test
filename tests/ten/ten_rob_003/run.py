import os, random, string
from pysys.constants import PASSED, FOREGROUND
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.emitter import EventEmitter, TransparentEventEmitter


class PySysTest(TenNetworkTest):
    NUM_CLIENTS = 10         # number of transactors and subscribers
    NUM_TRANSACTIONS = 250   # number of txs the transactors will perform

    def execute(self):
        # connect to network on the primary gateway and deploy contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        emitter = EventEmitter(self, web3, 100)
        emitter.deploy(network, account)
        transparent_emitter = TransparentEventEmitter(self, web3, 100)
        transparent_emitter.deploy(network, account)
        debugger_url = network.connection_url()

        # estimate how much gas each transactor will need
        rstr = self.rand_str()
        chain_id = network.chain_id()
        gas_price = web3.eth.gas_price
        params = {'from': account.address, 'chainId': chain_id, 'gasPrice': gas_price}
        limits = [emitter.contract.functions.emitSimpleEvent(1, rstr).estimate_gas(params)]
        limits.append(emitter.contract.functions.emitArrayEvent(1, [1,2], [rstr, rstr]).estimate_gas(params))
        limits.append(emitter.contract.functions.emitStructEvent(1, rstr).estimate_gas(params))
        limits.append(emitter.contract.functions.emitMappingEvent(1, [account.address], [200]).estimate_gas(params))
        gas_limit = max(limits)
        funds_needed = 1.1 * self.NUM_TRANSACTIONS * (gas_price * gas_limit)

        # set up the transactors and run the subscribers
        clients = []
        for id in range(0, self.NUM_CLIENTS):
            pk, account, network = self.setup_transactor(funds_needed)
            clients.append((id, pk, account, network))
            self.run_subscriber(network, emitter if random.randint(0,1) else transparent_emitter, account, id)
            self.run_lister(id, network.connection_url(), account.address)

        # start the pollers and the debugger
        self.run_debugger(emitter, debugger_url)
        self.run_poller_simple(network, emitter, transparent_emitter, 1)
        self.run_poller_all(network, emitter)

        # run the transactors serially in the foreground
        for id, pk, account, network in clients:
            self.run_transactor(id, transparent_emitter if id == 1 else emitter, pk, network, gas_limit)
            self.ratio_failures(file=os.path.join(self.output, 'transactor%d.out' % id))

        # assuming no other errors raised then we have passed
        self.addOutcome(PASSED)

    def setup_transactor(self, funds_needed):
        pk = self.get_ephemeral_pk()
        network = self.get_network_connection()
        web3, account = network.connect(self, private_key=pk, check_funds=False)
        self.distribute_native(account, web3.from_wei(funds_needed, 'ether'))
        return pk, account, network

    def run_transactor(self, id, emitter, pk, network, gas_limit):
        stdout = os.path.join(self.output, 'transactor%s.out' % id)
        stderr = os.path.join(self.output, 'transactor%s.err' % id)
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

    def run_debugger(self, emitter, url):
        stdout = os.path.join(self.output, 'debugger.out')
        stderr = os.path.join(self.output, 'debugger.err')
        script = os.path.join(self.input, 'debugger.py')
        args = []
        args.extend(['--network_http', url])
        args.extend(['--contract_address', '%s' % emitter.address])
        self.run_python(script, stdout, stderr, args)

    def run_lister(self, id, url, address):
        stdout = os.path.join(self.output, 'lister%s.out' % id)
        stderr = os.path.join(self.output, 'lister%s.err' % id)
        script = os.path.join(self.input, 'lister.py')
        args = []
        args.extend(['--network_http', url])
        args.extend(['--address', '%s' % address])
        self.run_python(script, stdout, stderr, args)

    def run_subscriber(self, network, emitter, account, id_filter):
        stdout = os.path.join(self.output, 'subscriber%d.out' % id_filter)
        stderr = os.path.join(self.output, 'subscriber%d.err' % id_filter)
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--contract_address', '%s' % emitter.address])
        args.extend(['--contract_abi', '%s' % emitter.abi_path])
        args.extend(['--id_filter', str(id_filter)])
        args.extend(['--address_filter', account.address])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Listening for filtered events...', timeout=10)

    def run_poller_simple(self, network, contract1, contract2, id_filter):
        stdout = os.path.join(self.output, 'poller_simple.out')
        stderr = os.path.join(self.output, 'poller_simple.err')
        script = os.path.join(self.input, 'poller_simple.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--contract1_address', '%s' % contract1.address])
        args.extend(['--contract1_abi', '%s' % contract1.abi_path])
        args.extend(['--contract2_address', '%s' % contract2.address])
        args.extend(['--contract2_abi', '%s' % contract2.abi_path])
        args.extend(['--id_filter', '%d' % id_filter])
        self.run_javascript(script, stdout, stderr, args)

    def run_poller_all(self, network, emitter):
        stdout = os.path.join(self.output, 'poller_all.out')
        stderr = os.path.join(self.output, 'poller_all.err')
        script = os.path.join(self.input, 'poller_all.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--contract_address', '%s' % emitter.address])
        args.extend(['--contract_abi', '%s' % emitter.abi_path])
        args.extend(['--id_range', '%d' % self.NUM_CLIENTS])
        self.run_javascript(script, stdout, stderr, args)

    def rand_str(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
