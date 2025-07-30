from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect players to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # player 1 deploys the transparent contract and performs some transactions against it
        self.log.info('')
        self.log.info('User deploys contract and submits transactions against it')
        storage = Storage(self, web3, 0)
        storage.deploy(network, account)

        hashes = []
        for i in range(1, 5):
            tx_receipt = network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS_LIMIT)
            hashes.append(tx_receipt.transactionHash.hex())

        # an ephemeral user connects
        web_usr, account_usr = network.connect(self, private_key=self.get_ephemeral_pk(), check_funds=True)

        # personal transactions for the ephemeral user with show public true
        self.log.info('')
        self.log.info('Personal transaction count (with public)')
        personal_txs = self.read_all_personal_txs(network, account_usr, show_public=True)
        personal_txs_hashes = [x['transactionHash'] for x in personal_txs]
        for h in hashes: self.assertTrue(h in personal_txs_hashes, assertMessage='%s is seen in list' % h)

        # personal transactions for the ephemeral user with show public false
        self.log.info('')
        self.log.info('Personal transaction count (no public)')
        personal_txs = self.read_all_personal_txs(network, account_usr, show_public=False)
        personal_txs_hashes = [x['transactionHash'] for x in personal_txs]
        for h in hashes: self.assertTrue(h not in personal_txs_hashes, assertMessage='%s is not seen in list' % h)
