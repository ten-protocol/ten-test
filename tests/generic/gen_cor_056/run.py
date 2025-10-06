from pysys.constants import PASSED
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.error import PayableConstructorRevert, SelfDestructOnDeploy


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        self.log.info('Expect the deployment to work, but contract to not exist')
        contract = SelfDestructOnDeploy(self, web3, account.address)
        contract.deploy(network, account)

        self.log.info('Expect deployment to fail')
        contract = PayableConstructorRevert(self, web3)
        contract.deploy(network, account, expect_fail=True)

        # assume passed if everything gets to this point fine
        self.addOutcome(PASSED)



