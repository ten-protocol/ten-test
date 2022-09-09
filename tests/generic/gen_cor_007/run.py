import re
from ethsys.basetest import EthereumTest
from ethsys.contracts.error.error import Error
from ethsys.networks.factory import NetworkFactory



class PySysTest(EthereumTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1()

        error = Error(self, web3, 'foo')
        error.deploy(network, account)

        self.log.info('Getting the contract bytecode ...')
        try:
            byte_code = web3.eth.getCode(error.contract_address).hex()[2:]
            self.assertTrue(byte_code in error.bytecode)
        except Exception as e:
            self.log.error('Error getting bytecode', e)