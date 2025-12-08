from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import TransparentGuessGame


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # user deploys the transparent contract and performs some transactions against it
        self.log.info('')
        self.log.info('User deploys transparent contract and submits 5 transactions against it')
        game = TransparentGuessGame(self, web3)
        game.deploy(network, account)

        hashes = []
        for i in range(1,5):
            tx_receipt = network.transact(self, web3, game.contract.functions.guess(i), account, game.GAS_LIMIT)
            hashes.append(tx_receipt.transactionHash.hex())

        # an ephemeral user connects
        web_usr, account_usr = network.connect(self, private_key=self.get_ephemeral_pk(), check_funds=True)

        # personal transactions for the ephemeral user with show public true
        self.log.info('')
        self.log.info('Personal transactions (with public)')
        personal_txs = self.read_all_personal_txs(network, account_usr, show_public=True)
        personal_txs_hashes = [x['transactionHash'] for x in personal_txs]
        for h in hashes: self.assertTrue(h in personal_txs_hashes, assertMessage='%s is seen in list' % h)

        # personal transactions for the ephemeral user with show public false
        self.log.info('')
        self.log.info('Personal transactions (no public)')
        personal_txs = self.read_all_personal_txs(network, account_usr, show_public=False)
        personal_txs_hashes = [x['transactionHash'] for x in personal_txs]
        for h in hashes: self.assertTrue(h not in personal_txs_hashes, assertMessage='%s is not seen in list' % h)
