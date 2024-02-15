import json
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        response = self.obscuro_config()
        sequencer_id = response["SequencerID"]
        l1_start_hash = response["L1StartHash"]
        l1_management_address = response["ManagementContractAddress"]
        l1_message_bus_address = response["MessageBusAddress"]
        l1_bridge_address = response["ImportantContracts"]["L1Bridge"]
        l1_xchain_messenger_address = response["ImportantContracts"]["L1CrossChainMessenger"]
        l2_message_bus_address = response["L2MessageBusAddress"]
        l2_bridge_address = response["ImportantContracts"]["L2Bridge"]
        l2_xchain_messenger_address = response["ImportantContracts"]["L2CrossChainMessenger"]

        self.log.info("")
        self.log.info("L1 and L2 contract addresses:")
        self.log.info("l1_management_address:       %s", l1_management_address)
        self.log.info("l1_message_bus_address:      %s", l1_message_bus_address)
        self.log.info("l1_bridge_address:           %s", l1_bridge_address)
        self.log.info("l1_xchain_messenger_address: %s", l1_xchain_messenger_address)
        self.log.info("l2_message_bus_address:      %s", l2_message_bus_address)
        self.log.info("l2_bridge_address:           %s", l2_bridge_address)
        self.log.info("l2_xchain_messenger_address: %s", l2_xchain_messenger_address)

        self.log.info("")
        self.log.info("Network node health:")
        self.log.info(self.obscuro_health())