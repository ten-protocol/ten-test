from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        # get the network and connect an ephemeral account
        network = self.get_network_connection()
        web3_usr, account_usr = network.connect(self, private_key=self.get_ephemeral_pk(), check_funds=False)

        # list the personal transactions for the user
        txs = self.scan_list_personal_txs(url=network.connection_url(), address=account_usr.address, offset=0, size=5)
        tx_hashs = [x['blockHash'] for x in txs['Receipts']]
        self.assertTrue(len(tx_hashs) == 0, assertMessage='Tx hashes returned should have length zero')

        # list the personal transactions never seen by the gateway
        unseen = web3_usr.eth.account.from_key(self.get_ephemeral_pk())
        error = self.scan_list_personal_txs(url=network.connection_url(), address=unseen.address, offset=0, size=5,
                                            return_error=True)
        self.assertTrue(error['message'] == 'unable to execute custom query: illegal access',
                        assertMessage='Error should state illegal access')
