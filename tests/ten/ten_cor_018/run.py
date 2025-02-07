import time
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage, KeyStorage
from ten.test.contracts.game import Game
from ten.test.contracts.calldata import CallData


class PySysTest(TenNetworkTest):

    def execute(self):
        run_time = int(time.time())

        # connect to network
        network = self.get_network_connection()
        web3, acnt = network.connect_account1(self)
        _, acnt2 = network.connect_account2(self)

        # the contracts to be deployed and measured
        storage = Storage(self, web3, 100)
        keystore = KeyStorage(self, web3)
        guessgame = Game(self, web3)
        calldata = CallData(self, web3)

        # the storage contract
        self.log.info('')
        self.log.info('Deploy the Storage contract and transact')
        storage.deploy(network, acnt, store=True)
        self.store_cost('Storage.deploy', run_time, network)
        network.transact(self, web3, storage.contract.functions.store(1), acnt, storage.GAS_LIMIT, store=True)
        self.store_cost('Storage.store', run_time, network)

        # the key storage contract
        self.log.info('')
        self.log.info('Deploy the KeyStorage contract and transact')
        keystore.deploy(network, acnt, store=True)
        self.store_cost('KeyStorage.deploy', run_time, network)
        network.transact(self, web3, keystore.contract.functions.storeItem(100), acnt, keystore.GAS_LIMIT, store=True)
        self.store_cost('KeyStorage.storeItem', run_time, network)
        network.transact(self, web3, keystore.contract.functions.setItem('k1', 101), acnt, keystore.GAS_LIMIT, store=True)
        self.store_cost('KeyStorage.setItem', run_time, network)

        # the guessing game contract
        self.log.info('')
        self.log.info('Deploy the Game contract and transact')
        guessgame.deploy(network, acnt, store=True)
        self.store_cost('Game.deploy', run_time, network)
        network.transact(self, web3, guessgame.contract.functions.guess(5), acnt, guessgame.GAS_LIMIT, store=True)
        self.store_cost('Game.guess', run_time, network)

        # the call data contract
        self.log.info('')
        self.log.info('Deploy the CallData contract and transact')
        calldata.deploy(network, acnt, store=True)
        self.store_cost('CallData.deploy', run_time, network)
        network.transact(self, web3,calldata.contract.functions.processLargeData([i for i in range(20)]),
                         acnt, calldata.GAS_LIMIT, store=True)
        self.store_cost('CallData.processLargeData', run_time, network)

        # a native funds transfer
        self.log.info('')
        self.log.info('Perform a native funds transfer')
        tx = {'to': acnt2.address, 'value': 1000, 'gasPrice': web3.eth.gas_price}
        tx['gas'] = web3.eth.estimate_gas(tx)
        receipt = network.tx(self, web3, tx, acnt, txstr='value transfer')
        self.txcosts_db.insert('Native.transfer', self.env, run_time, receipt.effectiveGasPrice, receipt.gasUsed, tx['gas'])

    def store_cost(self, name, run_time, network):
        estimate = network.last_tx[0]
        gas_price = network.last_tx[4].effectiveGasPrice
        gas_used = network.last_tx[4].gasUsed
        self.txcosts_db.insert(name, self.env, run_time, gas_price, gas_used, estimate)

