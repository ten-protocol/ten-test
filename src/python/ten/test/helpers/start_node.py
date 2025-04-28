import os
from web3 import Web3
from pysys.constants import FOREGROUND, PROJECT
from ten.test.utils.properties import Properties


class LocalValidatorNode:
    """A wrapper over starting and stopping an Obscuro node to a local testnet.

    Note that the L1 management and message bus contracts are taken from the properties at the moment, as is the
    sequencer id. These are liable to change and so this should be updated in the future. The L1 start block hash
    needs to be extracted from the hardhat deployer container that deployed into the local testnet.
    """
    def __init__(self, test, name, pk, http_port, ws_port, p2p_host, p2p_port, l1_start, env):
        """Create an instance of the helper. """
        self.test = test

        props = Properties()
        self.binary = props.go_binary()
        self.node_name = name
        self.node_type = 'validator'
        self.is_genesis = False
        self.num_enclaves = 1
        self.is_sgx_enabled = False
        self.enclave_docker_image = 'testnetobscuronet.azurecr.io/obscuronet/enclave:latest'
        self.host_docker_image = 'testnetobscuronet.azurecr.io/obscuronet/host:latest'
        self.l1_ws_url = "ws://eth2network:9000"
        self.host_http_port = http_port
        self.host_ws_port = ws_port
        self.host_p2p_port = p2p_port
        self.host_p2p_host = p2p_host
        self.enclave_http_port = 11000
        self.enclave_ws_port = 11001
        self.private_key = pk
        self.sequencer_addr = props.sequencer_address(test.env)
        #self.enclave_registry_addr =
        self.cross_chain_addr = props.l1_cross_chain_messenger_address()
        #self.da_registry_addr =
        #self.network_config_addr =
        #self.message_bus_contract_addr =
        #self.bridge_contract_addr =
        self.l1_start = l1_start
        #self.pccs_addr =
        self.edgeless_db_image = "ghcr.io/edgelesssys/edgelessdbsgx-4gb:v0.3.2"
        self.is_debug_namespace_enabled = False
        self.log_level = 3
        self.is_inbound_p2p_disabled = True
        self.batch_interval = 1
        self.host_id = Web3().eth.account.privateKeyToAccount(pk).address
        self.max_batch_interval = 1
        self.rollup_interval = 3
        self.l1_chain_id = 1337
        self.host_public_p2p_addr = '%s:%d' % (name, p2p_port)
        #self.postgres_db_host =
        self.l1_beacon_url = "eth2network:126000"
        #self.l1_blob_archive_url =
        #self.system_contracts_upgrader =

    def run(self):
        """Run the node. """
        arguments = ['run', './go/node/cmd']
        arguments.append('-is_genesis=%s' % str(self.is_genesis))
        arguments.append('-node_name=%s' % self.node_name)
        arguments.append('-node_type=%s' % self.node_type)
        arguments.append('-is_sgx_enabled=%s' % str(self.is_sgx_enabled))
        arguments.append('-host_id=%s' % self.host_id)
        arguments.append('-l1_host=%s' % self.l1_host)
        arguments.append('-management_contract_addr=%s' % self.management_contract_addr)
        arguments.append('-message_bus_contract_addr=%s' % self.message_bus_contract_addr)
        arguments.append('-l1_start=%s' % self.l1_start)
        arguments.append('-private_key=%s' % self.private_key)
        arguments.append('-sequencer_id=%s' % self.sequencer_id)
        arguments.append('-host_http_port=%s' % str(self.http_port))
        arguments.append('-host_ws_port=%s' % str(self.ws_port))
        arguments.append('-host_public_p2p_addr=%s' % str(self.host_public_p2p_addr))
        arguments.append('-host_p2p_port=%s' % str(self.host_p2p_port))
        arguments.append('-enclave_docker_image=%s' % self.enclave_docker_image)
        arguments.append('-host_docker_image=%s' % self.host_docker_image)
        arguments.append('start')

        stdout = os.path.join(self.test.output, 'start_node.out')
        stderr = os.path.join(self.test.output, 'start_node.err')
        dir = os.path.join(os.path.dirname(PROJECT.root), 'go-obscuro')

        hprocess = self.test.startProcess(command=self.binary, displayName='go',
                                          workingDir=dir, environs=os.environ, quiet=True,
                                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND)
        return hprocess
