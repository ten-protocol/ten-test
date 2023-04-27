from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        L1PKS = [Properties().l1_bridge_admin_pk(self.env)]
        L2PKS = [
            Properties().account1_1pk(), Properties().account2_1pk(),
            Properties().account3_1pk(), Properties().account4_1pk(),
            Properties().account1_2pk(), Properties().account2_2pk(),
            Properties().account3_2pk(), Properties().account4_2pk(),
            Properties().account1_3pk(), Properties().account2_3pk(),
            Properties().account3_3pk(), Properties().account4_3pk(),
            Properties().gg_appdev_pk(), Properties().gg_endusr_pk()
        ]

        network = NetworkFactory.get_l1_network(self)
        self.log.info('')
        self.log.info('Printing balance for the L1 accounts')
        for pk in L1PKS: network.connect(self, pk, check_funds=False)
        for pk in L2PKS: network.connect(self, pk, check_funds=False)

        network = NetworkFactory.get_network(self)
        self.log.info('')
        self.log.info('Printing balance for the L2 accounts')
        for pk in L2PKS: network.connect(self, pk, check_funds=False)