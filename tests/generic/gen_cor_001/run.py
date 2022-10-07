from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroTest):

    def execute(self):
        # connect to the network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)
        self.log.info('Using account with address %s' % account.address)

        # get the chain id
        chain_id = web3.eth.chain_id
        self.log.info('Chain id is %d' % chain_id)
        self.assertTrue(chain_id == network.chain_id())
