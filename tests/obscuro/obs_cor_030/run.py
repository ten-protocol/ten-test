import secrets
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.helpers.start_node import LocalValidatorNode
from obscuro.test.networks.obscuro import ObscuroL1Local
from obscuro.test.helpers.docker import Docker


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        # get the l1 start from the container logs
        container_id = Docker.get_id_from_name(test=self, name="hh-l1-deployer")
        output = Docker.get_logs(test=self, container_id=container_id)
        l1_start = Docker.get_l1_start(output)[0]
        self.log.info('Container %s shows l1 start as %s', container_id, l1_start)

        # create a new PK for the node and ensure it has funds
        network = ObscuroL1Local()
        node_pk = secrets.token_hex(32)
        _, node_account = network.connect(self, node_pk, check_funds=True)

        # start the node
        http_port = self.getNextAvailableTCPPort()
        ws_port = self.getNextAvailableTCPPort()
        p2p_port = self.getNextAvailableTCPPort()
        node = LocalValidatorNode(self, 'new_node', node_pk, http_port, ws_port, p2p_port, l1_start, self.env)
        node.run()
