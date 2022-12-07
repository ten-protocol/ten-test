from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.gas.gas_consumer import GasConsumer
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):
    # as previously reported on ganache and obscuro
    VALUES = [21208, 21296, 21275]

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)

        contract = GasConsumer(self, web3, 1)
        contract.deploy(network, account)

        # get the estimates and compare to previous references
        est_1 = contract.contract.functions.times_once().estimate_gas()
        est_2 = contract.contract.functions.times_twice().estimate_gas()
        est_3 = contract.contract.functions.times_thrice().estimate_gas()

        self.log.info("Estimate times_once:                          %d" % est_1)
        self.log.info("Estimate times_twice:                         %d" % est_2)
        self.log.info("Estimate times_thrice:                        %d" % est_3)
        self.assertTrue(est_1 == self.VALUES[0])
        self.assertTrue(est_2 == self.VALUES[1])
        self.assertTrue(est_3 == self.VALUES[2])

        # get the real values (no assert at the moment, just for interest)
        tx1 = network.transact(self, web3, contract.contract.functions.times_once(), account, contract.GAS)
        tx2 = network.transact(self, web3, contract.contract.functions.times_twice(), account, contract.GAS)
        tx3 = network.transact(self, web3, contract.contract.functions.times_thrice(), account, contract.GAS)

        self.log.info("Gas used times_once:                          %d" % int(tx1["gasUsed"]))
        self.log.info("Gas used times_twice:                         %d" % int(tx2["gasUsed"]))
        self.log.info("Gas used times_thrice:                        %d" % int(tx3["gasUsed"]))
