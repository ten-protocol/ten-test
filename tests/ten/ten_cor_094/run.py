import random, string
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.emitter import TransparentEventEmitter

def rstr():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        emitter = TransparentEventEmitter(self, web3)
        emitter.deploy(network, account)

        # transact and check event logs in the tx receipt
        self.log.info('Transact by calling emitArrayEvent')
        tx_receipt_1 = network.transact(self, web3,
                                        emitter.contract.functions.emitArrayEvent(int(1), [1,2], [rstr(), rstr()]),
                                        account, emitter.GAS_LIMIT)

        self.log.info('Transact by calling emitStructEvent')
        tx_receipt_2 = network.transact(self, web3,
                                        emitter.contract.functions.emitStructEvent(int(2), rstr()),
                                        account, emitter.GAS_LIMIT)

        self.log.info('Transact by calling emitMappingEvent')
        tx_receipt_3 = network.transact(self, web3,
                                        emitter.contract.functions.emitMappingEvent(int(3), [account.address], [random.randrange(100)]),
                                        account, emitter.GAS_LIMIT)
