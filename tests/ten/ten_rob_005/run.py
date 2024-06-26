import os, random, string, secrets, re
from pysys.constants import FAILED, PASSED, FOREGROUND
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.emitter import EventEmitter


class PySysTest(TenNetworkTest):
    CLIENTS = 10         # number of transactors and subscribers
    TRANSACTIONS = 200   # number of txs the transactors will perform

    def execute(self):
        # connect to network on the primary gateway and deploy contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        emitter = EventEmitter(self, web3, 100)
        emitter.deploy(network, account)

        # estimate how much gas each transactor will need
        rstr = self.randString()
        self.chain_id = network.chain_id()
        self.gas_price = web3.eth.gas_price
        params = {'from': account.address, 'chainId': web3.eth.chain_id, 'gasPrice': self.gas_price}
        limits = [emitter.contract.functions.emitSimpleEvent(1, rstr).estimate_gas(params)]
        limits.append(emitter.contract.functions.emitArrayEvent(1, [1,2], [rstr, rstr]).estimate_gas(params))
        limits.append(emitter.contract.functions.emitStructEvent(1, rstr).estimate_gas(params))
        limits.append(emitter.contract.functions.emitMappingEvent(1, [account.address], [200]).estimate_gas(params))
        self.gas_limit = max(limits)
        funds_needed = 1.1 * self.TRANSACTIONS * (self.gas_price * self.gas_limit)

        # setup the transactors and run the subscribers
        clients = []
        for id in range(0, self.CLIENTS):
            pk, account, network = self.setup_transactor(funds_needed)
            clients.append((id, pk, account, network))
            self.run_subscriber(network, emitter, account, id)

        # run the transactors serially in the foreground
        for id, pk, account, network in clients:
            self.run_transactor(id, emitter, pk, network)
            self.ratio_failures(file=os.path.join(self.output, 'transactor%d.out' % id))

        # assuming no other errors raised then we have passed
        self.addOutcome(PASSED)

    def setup_transactor(self, funds_needed):
        pk = secrets.token_hex(32)
        network = self.get_network_connection()
        web3, account = network.connect(self, private_key=pk, check_funds=False)
        self.distribute_native(account, web3.from_wei(funds_needed, 'ether'))
        return pk, account, network

    def run_transactor(self, id, emitter, pk, network):
        stdout = os.path.join(self.output, 'transactor%s.out' % id)
        stderr = os.path.join(self.output, 'transactor%s.err' % id)
        script = os.path.join(self.input, 'transactor.py')
        args = []
        args.extend(['--network_http', network.connection_url()])
        args.extend(['--chainId', '%s' % network.chain_id()])
        args.extend(['--pk', pk])
        args.extend(['--contract_address', '%s' % emitter.address])
        args.extend(['--contract_abi', '%s' % emitter.abi_path])
        args.extend(['--transactions', '%d' % self.TRANSACTIONS])
        args.extend(['--id', '%d' % id])
        args.extend(['--gas_limit', '%d' % self.gas_limit])
        self.run_python(script, stdout, stderr, args, state=FOREGROUND)

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

    def randString(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    def ratio_failures(self, file):
        ratio = 0
        regex = re.compile('Ratio failures = (?P<ratio>.*)$', re.M)
        with open(file, 'r') as fp:
            for line in fp.readlines():
                result = regex.search(line)
                if result is not None:
                    ratio = float(result.group('ratio'))
        self.log.info('Ratio of failures is %.2f' % ratio)
        if ratio > 0.05: self.addOutcome(FAILED, outcomeReason='Failure ratio > 0.05', abortOnError=False)
        return ratio