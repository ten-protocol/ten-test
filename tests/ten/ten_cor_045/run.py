from pysys.constants import PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage, KeyStorage
from ten.test.contracts.game import Game
from ten.test.contracts.calldata import CallData


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to networks
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
        self.check_dp('Storage.deploy', network, web3, storage, acnt)
        self.check_tx('Storage.store', network, web3, storage.contract.functions.store(1), acnt,
                      storage.GAS_LIMIT)

        # the key storage contract
        self.log.info('')
        self.log.info('Deploy the KeyStorage contract and transact')
        self.check_dp('KeyStorage.deploy', network, web3, keystore, acnt)
        self.check_tx('KeyStorage.storeItem', network, web3, keystore.contract.functions.storeItem(100), acnt,
                      keystore.GAS_LIMIT)
        self.check_tx('KeyStorage.setItem', network, web3, keystore.contract.functions.setItem('k1', 101), acnt,
                      keystore.GAS_LIMIT)

        # the guessing game contract
        self.log.info('')
        self.log.info('Deploy the Game contract and transact')
        self.check_dp('Game.deploy', network, web3, guessgame, acnt)
        self.check_tx('Game.guess', network, web3, guessgame.contract.functions.guess(5), acnt,
                      guessgame.GAS_LIMIT)

        # the call data contract
        self.log.info('')
        self.log.info('Deploy the CallData contract and transact')
        self.check_dp('CallData.deploy', network, web3, calldata, acnt)
        self.check_tx('CallData.processLargeData', network, web3,
                      calldata.contract.functions.processLargeData([i for i in range(20)]), acnt, calldata.GAS_LIMIT)

        # a native funds transfer
        self.log.info('')
        self.log.info('Perform a native funds transfer')
        before = web3.eth.get_balance(acnt.address)
        tx = {'to': acnt2.address, 'value': 1000, 'gasPrice': web3.eth.gas_price}
        tx['gas'] = web3.eth.estimate_gas(tx)
        receipt = network.tx(self, web3, tx, acnt, txstr='value transfer')
        after = web3.eth.get_balance(acnt.address)
        self.check_cost('Native.transfer', receipt, before-1000, after)


    def check_dp(self, name, network, web3, contract, account):
        before = web3.eth.get_balance(account.address)
        receipt = contract.deploy(network, account)
        after = web3.eth.get_balance(account.address)
        self.check_cost(name, receipt, before, after)

    def check_tx(self, name, network, web3, target, account, gas_limit):
        before = web3.eth.get_balance(account.address)
        receipt = network.transact(self, web3, target, account, gas_limit)
        after = web3.eth.get_balance(account.address)
        self.check_cost(name, receipt, before, after)

    def check_cost(self, name, receipt, balance_before, balance_after):
        computed = (receipt.gasUsed * receipt.effectiveGasPrice)
        actual = (balance_before - balance_after)
        self.log.info('Computed cost:      %d' % computed)
        self.log.info('Balance difference: %d' % actual)
        self.assertTrue(computed == actual, assertMessage='%s check on computed vs actual'%name)
