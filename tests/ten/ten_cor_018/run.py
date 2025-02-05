import time
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage, KeyStorage
from ten.test.contracts.game import Game
from ten.test.contracts.calldata import CallData

class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, acnt = network.connect_account1(self)

        self.log.info('')
        self.log.info('Deploy the Storage contract and transact')
        contract = Storage(self, web3, 100)
        self.store_cost('Storage.deploy', contract.deploy(network, acnt))
        self.store_cost('Storage.store',
                        network.transact(self,
                                         web3,
                                         contract.contract.functions.store(1),
                                         acnt,
                                         contract.GAS_LIMIT))

        self.log.info('')
        self.log.info('Deploy the KeyStorage contract and transact')
        contract = KeyStorage(self, web3)
        self.store_cost('KeyStorage.deploy', contract.deploy(network, acnt))
        self.store_cost('KeyStorage.storeItem',
                        network.transact(self,
                                         web3,
                                         contract.contract.functions.storeItem(100),
                                         acnt,
                                         contract.GAS_LIMIT))
        self.store_cost('KeyStorage.setItem',
                        network.transact(self,
                                         web3,
                                         contract.contract.functions.setItem('k1', 101),
                                         acnt,
                                         contract.GAS_LIMIT))

        self.log.info('')
        self.log.info('Deploy the Game contract and transact')
        contract = Game(self, web3)
        self.store_cost('Game.deploy', contract.deploy(network, acnt))
        self.store_cost('Game.guess',
                        network.transact(self,
                                         web3,
                                         contract.contract.functions.guess(5),
                                         acnt,
                                         contract.GAS_LIMIT))

        self.log.info('')
        self.log.info('Deploy the CallData contract and transact')
        contract = CallData(self, web3)
        self.store_cost('CallData.deploy', contract.deploy(network, acnt))
        self.store_cost('CallData.processLargeData',
                        network.transact(self,
                                         web3,contract.contract.functions.processLargeData([i for i in range(20)]),
                                         acnt,
                                         contract.GAS_LIMIT))

    def store_cost(self, name, receipt):
        self.txcosts_db.insert(name, self.env, int(time.time()), receipt.effectiveGasPrice, receipt.gasUsed)

