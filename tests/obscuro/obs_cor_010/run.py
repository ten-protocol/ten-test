import secrets, time
from pysys.constants import TIMEDOUT
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network_l2 = Obscuro
        network_l1 = NetworkFactory.get_l1_network(self.env)
        hoc_address_l2 = Properties().l2_hoc_token_address(self.env)
        hoc_address_l1 = Properties().l1_hoc_token_address(self.env)
        bridge_address_l1 = Properties().management_bridge_address(self.env)
        bridge_address_l2 = '0xdeB34A740ECa1eC42C8b8204CBEC0bA34FDD27f3'

        # the l1 distro account to hand out funds to the test user of this test
        web3_distro_l1, account_distro_l1 = network_l1.connect(self, Properties().distro_account_pk(self.env))

        # the test user l1 and l2 connections
        private_key = secrets.token_hex(32)
        web3_l2, account_l2 = network_l2.connect(self, private_key)
        web3_l1, account_l1 = network_l1.connect(self, private_key)

        # give the test user some ETH in l1
        self.fund_eth(network_l1, web3_distro_l1, account_distro_l1, web3_l1, account_l1, 0.01)

        # give the test user some HOC in l1
        d1 = self.get_token_balance(hoc_address_l1, web3_distro_l1, account_distro_l1)
        u1 = self.get_token_balance(hoc_address_l1, web3_l1, account_l1)
        self.transfer_token(network_l1, 'HOC', hoc_address_l1, web3_distro_l1, account_distro_l1, account_l1.address, 10)
        d2 = self.get_token_balance(hoc_address_l1, web3_distro_l1, account_distro_l1)
        u2 = self.get_token_balance(hoc_address_l1, web3_l1, account_l1)
        self.log.info("Balances B/A = (%d, %d), (%d, %d)" % (d1,u1,d2,u2))

        # transfer some HOC across the bridge
        self.transfer_token(network_l1, 'HOC', hoc_address_l1, web3_l1, account_l1, bridge_address_l1, 2)
        balance1 = self.wait_for_balance(hoc_address_l2, web3_l2, account_l2, 2)

        # give the test user some OBX in l1
        self.fund_obx(network_l2, web3_l2, account_l2, web3_l2.toWei(1, 'ether'))

        # transfer some HOC back
        self.transfer_token(network_l2, 'HOC', hoc_address_l2, web3_l2, account_l2, bridge_address_l2, 1)
        balance2 = self.wait_for_balance(hoc_address_l2, web3_l2, account_l2, 1)

        # l2 to l1 bridge transfers are not yet implemented
        self.assertTrue(balance1 == 2)
        self.assertTrue(balance2 == 1)

    def wait_for_balance(self, token_address, web3, account, amount, timeout=30):
        start_time = time.time()
        balance = self.get_token_balance(token_address, web3, account)
        while balance != amount:
            balance = self.get_token_balance(token_address, web3, account)
            if time.time() > start_time + timeout:
                self.log.info('Balance after time is %d' % balance)
                self.abort(TIMEDOUT, 'Timed out waiting for funds to be transferred')
            time.sleep(1)
        return balance