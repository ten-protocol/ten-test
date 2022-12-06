from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.gas.gas_consumer import GasConsumer
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)

        contract = GasConsumer(self, web3, 1)
        contract.deploy(network, account)

        add_once = contract.contract.functions.add_once().estimate_gas()
        add_twice = contract.contract.functions.add_twice().estimate_gas()
        add_thrice = contract.contract.functions.add_thrice().estimate_gas()
        add_three_times_with_a_long_name = contract.contract.functions.add_three_times_with_a_long_name().estimate_gas()

        self.log.info("Estimate add_once:                          %d" % add_once)
        self.log.info("Estimate add_twice:                         %d" % add_twice)
        self.log.info("Estimate add_thrice:                        %d" % add_thrice)
        self.log.info("Estimate add_three_times_with_a_long_name:  %d" % add_three_times_with_a_long_name)

        tx1 = network.transact(self, web3, contract.contract.functions.add_once(), account, contract.GAS)
        tx2 = network.transact(self, web3, contract.contract.functions.add_twice(), account, contract.GAS)
        tx3 = network.transact(self, web3, contract.contract.functions.add_thrice(), account, contract.GAS)
        tx4 = network.transact(self, web3, contract.contract.functions.add_three_times_with_a_long_name(), account, contract.GAS)

        self.log.info("Gas used add_once:                          %s" % tx1["gasUsed"])
        self.log.info("Gas used add_twice:                         %s" % tx2["gasUsed"])
        self.log.info("Gas used add_thrice:                        %s" % tx3["gasUsed"])
        self.log.info("Gas used add_three_times_with_a_long_name:  %s" % tx4["gasUsed"])
