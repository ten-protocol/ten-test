from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.error.error import Error
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        error = Error(self, web3, 'foo')
        error.deploy(network, account)

        self.log.info('Getting the contract bytecode ...')
        try:
            byte_code = web3.eth.get_code(error.contract_address).hex()[2:]
            self.assertTrue(byte_code in error.bytecode)
        except Exception as e:
            self.log.error('Error getting bytecode', e)