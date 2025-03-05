from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        # get the network and connect an ephemeral account
        network = self.get_network_connection()
        web3_usr, account_usr = network.connect(self, private_key=self.get_ephemeral_pk(), check_funds=False)

        # list the personal transactions for the user
        txs = self.scan_list_personal_transactions(url=network.connection_url(), address=account_usr.address,
                                                   offset=0,
                                                   size=5)
        tx_hashs = [x['blockHash'] for x in txs['Receipts']]
        self.assertTrue(len(tx_hashs) == 0)
