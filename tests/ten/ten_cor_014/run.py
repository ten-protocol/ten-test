from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        self.scan_list_personal_transactions(account.address)

