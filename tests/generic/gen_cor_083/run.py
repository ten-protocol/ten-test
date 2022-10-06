import os, requests
from obscuro.test.basetest import EthereumTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(EthereumTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        # deploy the storage contracts
        storage = Storage(self, web3, 0)
        storage.deploy(network, account)

        # run a background script
        port = self.getNextAvailableTCPPort()
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--script_server_port', '%d' % port])
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--network_ws', '%s' % network.connection_url(web_socket=True)])
        args.extend(['--filter_address', '%s' % storage.contract_address])
        args.extend(['--filter_topics', '%s' % web3.keccak(text='Stored(uint256)').hex()])
        if self.is_obscuro(): args.extend(['--pk_to_register', '%s' % Properties().account3pk()])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Subscriber listening for instructions', timeout=10)

        # perform some transactions on the key storage contract
        network.transact(self, web3, storage.contract.functions.store(100), account, storage.GAS)
        network.transact(self, web3, storage.contract.functions.store(101), account, storage.GAS)

        # subscribe
        self.subscribe(port, stdout)
        network.transact(self, web3, storage.contract.functions.store(102), account, storage.GAS)
        network.transact(self, web3, storage.contract.functions.store(103), account, storage.GAS)

        # unsubscribe
        self.unsubscribe(port, stdout)
        network.transact(self, web3, storage.contract.functions.store(104), account, storage.GAS)
        network.transact(self, web3, storage.contract.functions.store(105), account, storage.GAS)

        # wait and validate
        exprList=[]
        exprList.append('Stored value = 102')
        exprList.append('Stored value = 103')
        self.waitForGrep(file=stdout, expr='Stored value', condition='== 2', timeout=20)
        self.assertOrderedGrep(file=stdout, exprList=exprList)

    def subscribe(self, port, stdout):
        requests.post('http://127.0.0.1:%d' % port, data='SUBSCRIBE', headers={'Content-Type': 'text/plain'})
        self.waitForGrep(file=stdout, expr='Subscribed for event logs', timeout=10)

    def unsubscribe(self, port, stdout):
        requests.post('http://127.0.0.1:%d' % port, data='UNSUBSCRIBE', headers={'Content-Type': 'text/plain'})
        self.waitForGrep(file=stdout, expr='Unsubscribed for event logs', timeout=10)
