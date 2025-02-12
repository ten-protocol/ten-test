import time
from pysys.constants import PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage, KeyStorage
from ten.test.contracts.game import Game
from ten.test.contracts.calldata import CallData


class PySysTest(TenNetworkTest):

    def execute(self):
        _time = int(time.time())

        # connect to the L1 and L2 networks
        network = self.get_l1_network_connection()
        web3, _ = network.connect_account1(self, check_funds=False)
        l1gasprice = web3.eth.gas_price

        network = self.get_network_connection()
        web3, acnt = network.connect_account1(self)
        _, acnt2 = network.connect_account2(self)
        l2gasprice = web3.eth.gas_price

        # persist the l1 and l2 gas price for reference
        self.gas_db.insert(self.env, _time, l1gasprice, l2gasprice)

        # the contracts to be deployed and measured
        storage = Storage(self, web3, 100)
        keystore = KeyStorage(self, web3)
        guessgame = Game(self, web3)
        calldata = CallData(self, web3)

        # the storage contract
        self.log.info('')
        self.log.info('Deploy the Storage contract and transact')
        self.store_dp('Storage.deploy', _time, network, web3, storage, acnt)
        self.store_tx('Storage.store', _time, network, web3, storage.contract.functions.store(1), acnt, storage.GAS_LIMIT)

        # the key storage contract
        self.log.info('')
        self.log.info('Deploy the KeyStorage contract and transact')
        self.store_dp('KeyStorage.deploy', _time, network, web3, keystore, acnt)
        self.store_tx('KeyStorage.storeItem', _time, network, web3, keystore.contract.functions.storeItem(100), acnt, keystore.GAS_LIMIT)
        self.store_tx('KeyStorage.setItem', _time, network, web3, keystore.contract.functions.setItem('k1', 101), acnt, keystore.GAS_LIMIT)

        # the guessing game contract
        self.log.info('')
        self.log.info('Deploy the Game contract and transact')
        self.store_dp('Game.deploy', _time, network, web3, guessgame, acnt)
        self.store_tx('Game.guess', _time, network, web3, guessgame.contract.functions.guess(5), acnt, guessgame.GAS_LIMIT)

        # the call data contract
        self.log.info('')
        self.log.info('Deploy the CallData contract and transact')
        self.store_dp('CallData.deploy', _time, network, web3, calldata, acnt)
        self.store_tx('CallData.processLargeData', _time, network, web3,
                      calldata.contract.functions.processLargeData([i for i in range(20)]), acnt, calldata.GAS_LIMIT)

        # a native funds transfer
        self.log.info('')
        self.log.info('Perform a native funds transfer')
        tx = {'to': acnt2.address, 'value': 1000, 'gasPrice': web3.eth.gas_price}
        tx['gas'] = web3.eth.estimate_gas(tx)
        receipt = network.tx(self, web3, tx, acnt, txstr='value transfer')
        self.txcosts_db.insert('Native.transfer', self.env, _time, receipt.effectiveGasPrice, receipt.gasUsed, tx['gas'])

        # pass if no errors
        self.addOutcome(PASSED)

    def store_dp(self, name, run_time, network, web3, contract, account):
        before = web3.eth.get_balance(account.address)
        contract.deploy(network, account, store=True)
        after = web3.eth.get_balance(account.address)
        self.store_cost(name, run_time, network, before, after)

    def store_tx(self, name, run_time, network, web3, target, account, gas_limit):
        before = web3.eth.get_balance(account.address)
        network.transact(self, web3, target, account, gas_limit, store=True)
        after = web3.eth.get_balance(account.address)
        self.store_cost(name, run_time, network, before, after)

    def store_cost(self, name, run_time, network, balance_before, balance_after):
        estimate = network.last_tx[0]
        gas_price = network.last_tx[4].effectiveGasPrice
        gas_used = network.last_tx[4].gasUsed
        self.log.info('Computed cost:      %d' % (gas_used*gas_price))
        self.log.info('Balance difference: %d' % (balance_before - balance_after))
        self.txcosts_db.insert(name, self.env, run_time, gas_price, gas_used, estimate)
