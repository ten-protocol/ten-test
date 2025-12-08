from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.error import Error


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network and deploy the contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        error = Error(self, web3)
        error.deploy(network, account)

        self.log.info('Getting the contract bytecode ...')
        try:
            byte_code = web3.eth.get_code(error.address).hex()[2:]
            self.assertTrue(byte_code in error.bytecode)
        except Exception as e:
            self.log.error('Error getting bytecode', e)