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

        log = DockerHelper.container_logs(self, 'validator-enclave-0')
        restarts = self.count_string_in_file(log, 'Server started.')
        self.log.info('Container has previous restarts %d' % restarts)

        DockerHelper.container_stop(self, 'validator-enclave-0')
        try:
            network.transact(self, web3, storage.contract.functions.store(3), account, storage.GAS_LIMIT)
            value = storage.contract.functions.retrieve().call()
            self.log.info('Retrieved value is %d' % value)
        except ValueError as error:
            self.log.warn('Unable to perform transaction')

        DockerHelper.container_start(self, 'validator-enclave-0')
        try:
            network.transact(self, web3, storage.contract.functions.store(3), account, storage.GAS_LIMIT)
            value = storage.contract.functions.retrieve().call()
            self.log.info('Retrieved value is %d' % value)
        except ValueError as error:
            self.log.warn('Unable to perform transaction')

    def count_string_in_file(self, filename, search_string):
        try:
            with open(filename, 'r') as file:
                content = file.read()
                count = content.count(search_string)
            return count
        except FileNotFoundError:
            return None