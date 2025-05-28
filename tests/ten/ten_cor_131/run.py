from pysys.constants import TIMEDOUT
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.system import TenSystemCallsCaller


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()

        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        caller = TenSystemCallsCaller(self, web3)
        caller.deploy(network, account)

        self.same_block(web3, caller, props)
        self.across_blocks(web3, caller, props)

    def same_block(self, web3, caller, props):
        count = 0
        while True or (count < 20):
            block_num = web3.eth.get_block_number()
            rand1 = caller.contract.functions.callRandomNumber(props.L2TenSystemCalls).call()
            if block_num == web3.eth.get_block_number():
                rand2 = caller.contract.functions.callRandomNumber(props.L2TenSystemCalls).call()
                self.log.info('Numbers both obtained from block number %d' % block_num)
                self.assertTrue(rand1 == rand2, assertMessage='Values should be the same within same block')
                return
            count = count + 1
        self.log.warn('Unable to obtain numbers within same block number')
        self.addOutcome(TIMEDOUT)

    def across_blocks(self, web3, caller, props):
        count = 0
        rand1 = caller.contract.functions.callRandomNumber(props.L2TenSystemCalls).call()
        block_num = web3.eth.get_block_number()
        while True or (count < 20):
            if web3.eth.get_block_number() > block_num:
                rand2 = caller.contract.functions.callRandomNumber(props.L2TenSystemCalls).call()
                self.log.info('Numbers obtained from block number %d and higher' % block_num)
                self.assertTrue(rand1 != rand2, assertMessage='Values should be different across blocks')
                return
            count = count + 1
            self.wait(float(self.block_time))
        self.log.warn('Unable to obtain numbers across different block numbers')
        self.addOutcome(TIMEDOUT)