from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):

    def execute(self):
        network = Obscuro
        web3_deploy, deploy_account = network.connect(self, Properties().funded_deployment_account_pk(self.env))
        self.fund_obx(network, web3_deploy, deploy_account)

