from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        self.log.info('HERE 1')
        network = self.get_network_connection()
        self.log.info('HERE 2')
        web3, account = network.connect_account1(self)
        self.log.info('HERE 3')

        # get the chain id
        chain_id = web3.eth.chain_id
        self.log.info('Returned chain id is %d', chain_id)
        self.assertTrue(chain_id == network.chain_id())
