from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        PKS = [
            Properties().account1_1pk(), Properties().account2_1pk(),
            Properties().account3_1pk(), Properties().account4_1pk(),
            Properties().account1_2pk(), Properties().account2_2pk(),
            Properties().account3_2pk(), Properties().account4_2pk(),
            Properties().account1_3pk(), Properties().account2_3pk(),
            Properties().account3_3pk(), Properties().account4_3pk(),
            Properties().account3_3pk(), Properties().gg_appdev_pk(),
            Properties().gg_appdev_pk(), Properties().gg_endusr_pk()
        ]

        network = NetworkFactory.get_network(self)
        for pk in PKS:
            account = Web3().eth.account.privateKeyToAccount(pk)
            self.fund_obx(network, account, 100)
