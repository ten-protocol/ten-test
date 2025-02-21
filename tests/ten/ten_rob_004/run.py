from ten.test.utils.docker import DockerHelper
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT)
        value = storage.contract.functions.retrieve().call()
        self.log.info('Retrieved value is %d' % value)

        DockerHelper.container_stop(self, 'validator-enclave-0')
        try:
            network.transact(self, web3, storage.contract.functions.store(3), account, storage.GAS_LIMIT)
            value = storage.contract.functions.retrieve().call()
            self.log.info('Retrieved value is %d' % value)
        except ValueError as error:
            self.log.warn('Unable to perform transaction')

        DockerHelper.container_start(self, 'validator-enclave-0', search_msg='Server started.')
        try:
            network.transact(self, web3, storage.contract.functions.store(3), account, storage.GAS_LIMIT)
            value = storage.contract.functions.retrieve().call()
            self.log.info('Retrieved value is %d' % value)
        except ValueError as error:
            self.log.warn('Unable to perform transaction')
