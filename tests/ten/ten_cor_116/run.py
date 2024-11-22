from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.storage import StorageTwoPhaseReceiveWithRevert


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = StorageTwoPhaseReceiveWithRevert(self, web3, 100, Properties().L2PublicCallbacks)
        storage.deploy(network, account)
        self.log.info('Call shows value: %d', storage.contract.functions.retrieve().call())

        # transact
        target = storage.contract.functions.store(1)
        params = {'gasPrice': web3.eth.gas_price, 'value': web3.to_wei(0.01, 'ether')}
        gas_estimate = target.estimate_gas(params)
        params['gas'] = int(1.1 * gas_estimate)
        build_tx = target.build_transaction(params)
        network.tx(self, web3, build_tx, account)
        self.log.info('Call shows value: %d', storage.contract.functions.retrieve().call())

