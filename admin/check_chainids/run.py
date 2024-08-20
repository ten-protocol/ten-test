from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network l2
        network_l1 = self.get_l1_network_connection()
        web3, account = network_l1.connect_account1(self)
        self.log.info('L1 returned chain id is %d', web3.eth.chain_id)

        # connect to the network l2
        network_l2 = self.get_network_connection()
        web3, account = network_l2.connect_account1(self)
        self.log.info('L2 returned chain id is %d', web3.eth.chain_id)
