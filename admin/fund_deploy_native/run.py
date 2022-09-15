from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):

    def execute(self):
        network = Obscuro
        web3_deploy, deploy_account = network.connect(Properties().funded_deployment_account_pk(self.env))
        web3_faucet, faucet_account = network.connect(Properties().faucet_pk(self.env))
        self.fund_obx(network, web3_deploy, deploy_account, web3_faucet, faucet_account)

