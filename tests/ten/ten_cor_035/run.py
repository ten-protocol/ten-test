import os, json
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import TransparentGuessGame
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect players to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # player 1 deploys the transparent contract and performs some transactions against it
        self.log.info('')
        self.log.info('User deploys transparent contract and submits 5 transactions against it')
        game = TransparentGuessGame(self, web3)
        game.deploy(network, account)

        hashes = []
        for i in range(1,5):
            tx_receipt = network.transact(self, web3, game.contract.functions.guess(i), account, game.GAS_LIMIT)
            hashes.append(tx_receipt.transactionHash.hex())

        # an ephemeral user connects and requests the public transactions (last 10, 2 pages max 5 in each)
        self.log.info('')
        self.log.info('Ephemeral user gets last two pages of personal transactions')
        web_usr, account_usr = network.connect(self, private_key=self.get_ephemeral_pk(), check_funds=True)

        # personal transactions for the ephemeral user with show public true
        self.log.info('')
        personal_txs_count = self.scan_list_personal_transactions(url=network.connection_url(), address=account_usr.address,
                                                                  show_public=True, offset=0, size=1)['Total']
        self.log.info('Personal transaction count (with public)is %d' % personal_txs_count)

        personal_txs = self.scan_list_personal_transactions(url=network.connection_url(), address=account_usr.address,
                                                            show_public=True, offset=0, size=personal_txs_count)['Receipts']
        personal_txs_hashes = [x['transactionHash'] for x in personal_txs]
        for h in hashes:
            self.assertTrue(h in personal_txs_hashes, assertMessage='%s is seen in list' % h)

        # personal transactions for the ephemeral user with show public false
        self.log.info('')
        personal_txs_count = self.scan_list_personal_transactions(url=network.connection_url(), address=account_usr.address,
                                                                      show_public=False, offset=0, size=1)['Total']
        self.log.info('Personal transaction count (no public) is %d' % personal_txs_count)

        personal_txs = self.scan_list_personal_transactions(url=network.connection_url(), address=account_usr.address,
                                                            show_public=False, offset=0, size=personal_txs_count)['Receipts']
        personal_txs_hashes = [x['transactionHash'] for x in personal_txs]
        for h in hashes:
            self.assertTrue(h not in personal_txs_hashes, assertMessage='%s is not seen in list' % h)