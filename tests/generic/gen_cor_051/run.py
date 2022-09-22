import re
from ethsys.basetest import EthereumTest
from ethsys.contracts.error.error import Error
from ethsys.networks.factory import NetworkFactory


class PySysTest(EthereumTest):
    WEBSOCKET = False

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)

        error = Error(self, web3, 'foo')
        error.deploy(network, account)

        # force a require @todo add in once debug_traceTransaction is enabled
        tx_receipt = network.transact(self, web3, error.contract.functions.set_key(""), account, error.GAS)

        params = {"disableStorage": "true", "disableMemory": "false", "disableStack": "false", "fullStorage": "false"}
        response = web3.manager.request_blocking('debug_traceTransaction', [tx_receipt.blockHash.hex(), params])
        self.log.info('Response is %s' % response)

