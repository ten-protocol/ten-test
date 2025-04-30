import os
from web3 import Web3
from pysys.constants import FOREGROUND, PROJECT
from ten.test.utils.properties import Properties


class LocalValidatorNode:
    """A wrapper over starting and stopping a Validator node to a local testnet."""

    def __init__(self, test, name, pk, http_port, ws_port, p2p_host, p2p_port):
        """Create an instance."""
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
        self.enclave_registry_addr = props.l1_enclave_registry_address()
        self.cross_chain_addr = props.l1_cross_chain_messenger_address()
        self.da_registry_addr = props.l1_data_availability_registry_address()
        self.network_config_addr = props.l1_network_config_address()
        self.message_bus_contract_addr = props.l1_message_bus_address()
        self.bridge_contract_addr = props.l1_bridge_address()
        self.l1_start = props.l1_start_hash()
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
        self.l1_beacon_url = "eth2network:126000"
        self.system_contracts_upgrader = '0xA58C60cc047592DE97BF1E8d2f225Fc5D959De77'
        # start up options not needed are;
        #   self.pccs_addr
        #   self.postgres_db_host
        #   self.l1_blob_archive_url

    def run(self):
        """Run the node. """
        arguments = ['run', './go/node/cmd']
        arguments.append('-node_name=%s' % self.node_name)
        arguments.append('-node_type=%s' % self.node_type)
        arguments.append('-is_genesis=%s' % self.is_genesis)
        arguments.append('-num_enclaves=%d' % self.num_enclaves)
        arguments.append('-is_sgx_enabled=%s' % self.is_sgx_enabled)
        arguments.append('-enclave_docker_image=%s' % self.enclave_docker_image)
        arguments.append('-host_docker_image=%s' % self.host_docker_image)
        arguments.append('-l1_ws_url=%s' % self.l1_ws_url)
        arguments.append('-host_http_port=%d' % self.host_http_port)
        arguments.append('-host_ws_port=%d' % self.host_ws_port)
        arguments.append('-host_p2p_port=%d' % self.host_p2p_port)
        arguments.append('-host_p2p_host=%d' % self.host_p2p_host)
        arguments.append('-enclave_http_port=%d' % self.enclave_http_port)
        arguments.append('-enclave_ws_port=%s' % self.enclave_ws_port)
        arguments.append('-private_key=%s' % self.private_key)
        arguments.append('-sequencer_addr=%s' % self.sequencer_addr)
        arguments.append('-enclave_registry_addr=%s' % self.enclave_registry_addr)
        arguments.append('-cross_chain_addr=%s' % self.cross_chain_addr)
        arguments.append('-da_registry_addr=%s' % self.da_registry_addr)
        arguments.append('-network_config_addr=%s' % self.network_config_addr)
        arguments.append('-message_bus_contract_addr=%s' % self.message_bus_contract_addr)
        arguments.append('-bridge_contract_addr=%s' % self.bridge_contract_addr)
        arguments.append('-l1_start=%s' % self.l1_start)
        arguments.append('-edgeless_db_image=%s' % self.edgeless_db_image)
        arguments.append('-is_debug_namespace_enabled=%s' % self.is_debug_namespace_enabled)
        arguments.append('-log_level=%d' % self.log_level)
        arguments.append('-is_inbound_p2p_disabled=%s' % self.is_inbound_p2p_disabled)
        arguments.append('-batch_interval=%d' % self.batch_interval)
        arguments.append('-host_id=%d' % self.host_id)
        arguments.append('-max_batch_interval=%d' % self.max_batch_interval)
        arguments.append('-rollup_interval=%d' % self.rollup_interval)
        arguments.append('-l1_chain_id=%d' % self.l1_chain_id)
        arguments.append('-host_public_p2p_addr=%s' % self.host_public_p2p_addr)
        arguments.append('-l1_beacon_url=%s' % self.l1_beacon_url)
        arguments.append('-system_contracts_upgrader=%s' % self.system_contracts_upgrader)
        arguments.append('start')

        stdout = os.path.join(self.test.output, 'start_node.out')
        stderr = os.path.join(self.test.output, 'start_node.err')
        dir = os.path.join(os.path.dirname(PROJECT.root), 'go-ten')

        hprocess = self.test.startProcess(command=self.binary, displayName='go',
                                          workingDir=dir, environs=os.environ, quiet=True,
                                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND)
        return hprocess
