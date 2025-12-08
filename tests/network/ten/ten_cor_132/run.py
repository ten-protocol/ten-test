from web3._utils.events import EventLogErrorFlags
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.system import TenSystemCallsCaller


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()

        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        caller = TenSystemCallsCaller(self, web3)
        caller.deploy(network, account)

        # send in the transactions
        id = 1
        target = caller.contract.functions.emitRandomNumber(id, props.L2TenSystemCalls)
        receipt1 = network.transact(self, web3, target, account, caller.GAS_LIMIT)
        logs1 = caller.contract.events.RandomNumber().process_receipt(receipt1, EventLogErrorFlags.Discard)
        random1 = logs1[0]['args']['random_num']
        block1 = logs1[0]['blockNumber']
        self.assertTrue(logs1[0]['args']['id'] == id, assertMessage='The id should match')

        id = 2
        target = caller.contract.functions.emitRandomNumber(id, props.L2TenSystemCalls)
        receipt2 = network.transact(self, web3, target, account, caller.GAS_LIMIT)
        logs2 = caller.contract.events.RandomNumber().process_receipt(receipt2, EventLogErrorFlags.Discard)
        random2 = logs2[0]['args']['random_num']
        block2 = logs2[0]['blockNumber']
        self.assertTrue(logs2[0]['args']['id'] == id, assertMessage='The id should match')

        self.log.info('Random1: %d' % random1)
        self.log.info('Block1:  %d' % block1)
        self.log.info('Random2: %d' % random2)
        self.log.info('Block2:  %d' % block2)
        self.assertTrue(random1 != random2, assertMessage='The random numbers should be different')
