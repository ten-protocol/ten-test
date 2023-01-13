from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.error.error import Error
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self)
        network.add_ws_proxy(self)
        web3, account = network.connect_account1(self, web_socket=True)

        error = Error(self, web3, 'foo')
        error.deploy(network, account)

        # force a require @todo add in once debug_traceTransaction is enabled
        tx_receipt = network.transact(self, web3, error.contract.functions.set_key(""), account, error.GAS_LIMIT)

        params = {"disableStorage": "true", "disableMemory": "false", "disableStack": "false", "fullStorage": "false"}
        response = web3.manager.request_blocking('debug_traceTransaction', [tx_receipt.blockHash.hex(), params])
        self.log.info('Response is %s' % response)

