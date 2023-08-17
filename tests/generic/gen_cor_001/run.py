from obscuro.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # get the chain id
        chain_id = web3.eth.chain_id
        self.log.info('Chain id is %d', chain_id)
        self.assertTrue(chain_id == network.chain_id())
