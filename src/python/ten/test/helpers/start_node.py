
class Node:
    """A wrapper over starting and stopping a Ten node.

    go run /home/obscuro/go-ten/go/node/cmd \
     -is_genesis="false" \
     -node_type=validator \
     -is_sgx_enabled="true" \
     -host_id="0xD5C925bb6147aF6b6bB6086dC6f7B12faa1ab0ff" \
     -l1_host="dev-testnet-eth2network.uksouth.azurecontainer.io" \
     -management_contract_addr="0x7d13152F196bDEebBD6CC53CD43e0CdAf97CbdE6" \ L1ManagementAddress
     -message_bus_contract_addr="0x426E82B481E2d0Bd6A1664Cccb24FFc76C0AD2f9" \ L1MessageBusAddress
     -l1_start="0x190f89a5f68a880f1cd2a67e0ed17980c7f012503279a764acc78a538d7e188f" \ L1StartAddress
     -private_key="f19601351ab594b04f21bc1d577e03cc62290a5efea8198af8bdfb19dad035b3" \
     -sequencer_id="0xc272459070A881BfA28aB3E810f9b19E4F468531" \
     -host_public_p2p_addr="$(curl https://ipinfo.io/ip):10000" \
     -host_p2p_port=10000 \
     -enclave_docker_image="testnetobscuronet.azurecr.io/obscuronet/dev_enclave:latest" \
     -host_docker_image="testnetobscuronet.azurecr.io/obscuronet/dev_host:latest" \
     start

    """

    def __init__(self):
        pass