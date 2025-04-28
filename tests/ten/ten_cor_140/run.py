import secrets
from ten.test.basetest import TenNetworkTest
from ten.test.helpers.start_node import LocalValidatorNode
from ten.test.networks.ten import TenL1Geth
from ten.test.helpers.docker import Docker


class PySysTest(TenNetworkTest):

    def execute(self):
        # get the l1 start from the container logs
        container_id = Docker.get_id_from_name(test=self, name="hh-l1-deployer")
        output = Docker.get_logs(test=self, container_id=container_id)
        l1_start = Docker.get_l1_start(output)[0]

        # create a new PK for the node and ensure it has funds
        network = TenL1Geth(self)
        node_pk = secrets.token_hex(32)
        _, node_account = network.connect(self, node_pk, check_funds=True)

        # start the node
        http_port = self.getNextAvailableTCPPort()
        ws_port = self.getNextAvailableTCPPort()
        p2p_port = self.getNextAvailableTCPPort()
        node = LocalValidatorNode(self, 'new_node', node_pk, http_port, ws_port, p2p_port, l1_start, self.env)
        node.run()

        host_id = Docker.get_id_from_name(test=self, name="new_node-host")
        enclave_id = Docker.get_id_from_name(test=self, name="new_node-enclave")
        self.log.info('Node node started, host_id=%s, enclave_id=%s', host_id, enclave_id)

        # stop the node containers
        self.wait(20)
        Docker.stop_and_remove(self, host_id)
        Docker.stop_and_remove(self, enclave_id)
