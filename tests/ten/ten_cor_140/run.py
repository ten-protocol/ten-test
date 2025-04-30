import secrets
from ten.test.basetest import TenNetworkTest
from ten.test.helpers.start_node import LocalValidatorNode
from ten.test.networks.ten import TenL1Geth
from ten.test.utils.docker import DockerHelper


class PySysTest(TenNetworkTest):

    def execute(self):
        # create a new PK for the node and ensure it has funds
        network = TenL1Geth(self)
        node_pk = secrets.token_hex(32)
        _, node_account = network.connect(self, node_pk, check_funds=True)

        # start the node
        http_port = self.getNextAvailableTCPPort()
        ws_port = self.getNextAvailableTCPPort()
        p2p_port = self.getNextAvailableTCPPort()
        node = LocalValidatorNode(self, 'new_node', node_pk, http_port, ws_port, p2p_port, self.env)
        node.run()

        host_id = DockerHelper.container_id(test=self, name="new_node-host")
        enclave_id = DockerHelper.container_id(test=self, name="new_node-enclave")
        self.log.info('Validator node started, host_id=%s, enclave_id=%s', host_id, enclave_id)


