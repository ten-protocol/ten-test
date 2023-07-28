import os
from web3 import Web3
from pysys.constants import FOREGROUND
from obscuro.test.utils.properties import Properties


class Node:
    """A wrapper over starting and stopping an Obscuro node.

    go run /home/obscuro/go-obscuro/go/node/cmd \
     -is_genesis="false" \
     -node_type=validator \
     -is_sgx_enabled="false" \
     -host_id="0x3afFe57d8795D9eb88166AE50226cFf48dd39e16" \
     -l1_host="eth2network" \
     -management_contract_addr="0xeDa66Cc53bd2f26896f6Ba6b736B1Ca325DE04eF" \
     -message_bus_contract_addr="0xFD03804faCA2538F4633B3EBdfEfc38adafa259B" \
     -l1_start="0xbd0ab494557d9f2f3d19c885e183fd2d2083d8ea2727412e5fc3f5d44b797d4c" \
     -private_key="37782e8b21d996e2668ae353b48ab1208c6e4689e2d4c542861af4fc77bad4d9" \
     -sequencer_id="0x0654D8B60033144D567f25bF41baC1FB0D60F23B" \
     -host_public_p2p_addr="validator-host-two" \
     -host_p2p_port=16010 \
     -enclave_docker_image="testnetobscuronet.azurecr.io/obscuronet/enclave:latest" \
     -host_docker_image="testnetobscuronet.azurecr.io/obscuronet/host:latest" \
     start

    """

    def __init__(self, test, pk, p2p_address, p2p_port, l1_host, env):
        """Create an instance of the wrapper. """
        self.test = test

        props = Properties()
        self.binary = props.go_binary()
        self.is_genesis = False
        self.node_type = 'validator'
        self.is_sgx_enabled = False
        self.host_id = Web3().eth.account.privateKeyToAccount(pk).address
        self.l1_host = l1_host
        self.management_contract_addr = props.l1_management_address(env)
        self.message_bus_contract_addr = props.l1_message_bus_address(env)
        self.l1_start = props.l1_start_block_hash(env)
        self.private_key = pk
        self.sequencer_id = props.sequencer_id(env)
        self.host_public_p2p_addr = p2p_address
        self.host_p2p_port = p2p_port
        self.enclave_docker_image = 'testnetobscuronet.azurecr.io/obscuronet/enclave:latest'
        self.host_docker_image = 'testnetobscuronet.azurecr.io/obscuronet/host:latest'

    def run(self):
        """Run an instance of the wallet extension. """
        arguments = []
        arguments.extend(('-is_genesis', str(self.is_genesis)))
        arguments.extend(('-node_type', self.node_type))
        arguments.extend(('-is_sgx_enabled', str(self.is_sgx_enabled)))
        arguments.extend(('-host_id', self.host_id))
        arguments.extend(('-l1_host', self.l1_host))
        arguments.extend(('-management_contract_addr', self.management_contract_addr))
        arguments.extend(('-message_bus_contract_addr', self.message_bus_contract_addr))
        arguments.extend(('-l1_start', self.l1_start))
        arguments.extend(('-private_key', self.private_key))
        arguments.extend(('-sequencer_id', self.sequencer_id))
        arguments.extend(('-host_public_p2p_addr', self.host_public_p2p_addr))
        arguments.extend(('-host_p2p_port', self.host_p2p_port))
        arguments.extend(('-enclave_docker_image', self.enclave_docker_image))
        arguments.extend(('-host_docker_image', self.host_docker_image))

        stdout = os.path.join(self.test.output, 'start_node.out')
        stderr = os.path.join(self.test.output, 'start_node.err')

        hprocess = self.test.startProcess(command=self.binary, displayName='wallet_extension',
                                          workingDir=self.test.output, environs=os.environ, quiet=True,
                                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND)
        return hprocess
