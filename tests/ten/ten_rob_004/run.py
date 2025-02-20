from ten.test.utils.docker import DockerHelper
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        _, _ = network.connect_account1(self)

        enclave_id = DockerHelper.container_id(self, 'validator-enclave-0')
        self.log.info('Validator enclave container id is %s' % enclave_id)