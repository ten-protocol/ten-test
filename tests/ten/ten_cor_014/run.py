from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage
from ten.test.contracts.calldata import CallData


class PySysTest(TenNetworkTest):

    def execute(self):
        # get the network, and deploy the contracts
        network = self.get_network_connection()
        web3_deploy, account_deploy = network.connect_account1(self)
        storage = Storage(self, web3_deploy, 0)
        storage.deploy(network, account_deploy)
        calldata = CallData(self, web3_deploy)
        calldata.deploy(network, account_deploy)

        # connect as an ephemeral test user and transact against the contracts
        self.log.info('')
        self.log.info('Create the ephemeral user 1 and fund them')
        pk = self.get_ephemeral_pk()
        web_usr1, account_usr1 = network.connect(self, private_key=pk, check_funds=True)

        self.log.info('')
        self.log.info('User 1 performs three contract calls')
        tx_receipt1 = network.transact(self, web_usr1, storage.contract.functions.store(1), account_usr1, storage.GAS_LIMIT)
        tx_receipt2 = network.transact(self, web_usr1, storage.contract.functions.store(2), account_usr1, storage.GAS_LIMIT)
        tx_receipt3 = network.transact(self, web_usr1, calldata.contract.functions.processLargeData([i for i in range(20)]), account_usr1, storage.GAS_LIMIT)

        # connect as an ephemeral test user and transfer funds
        self.log.info('')
        self.log.info('Create the ephemeral user 2 and fund them')
        pk2 = self.get_ephemeral_pk()
        web3_usr2, account_usr2 = network.connect(self, private_key=pk2, check_funds=True)

        self.log.info('')
        self.log.info('User 2 performs a native transfer to user 1')
        transfer_amount = web3_usr2.to_wei(0.001, 'ether')
        tx = {'to': account_usr1.address,'value': transfer_amount,'gasPrice': web3_usr2.eth.gas_price}
        tx['gas'] = web3_usr2.eth.estimate_gas(tx)
        tx_receipt4 = network.tx(self, web3_usr2, tx, account_usr2, verbose=True, txstr='transfer from account_usr2 to account_usr')

        # log out the transaction block hashes and tx hashes from requesting the list of personal transactions
        # excluding the synthetic ones (these are the zen tokens that accrue for each transaction made)
        # remember public transactions are not the same as personal (public means an open contract or one that emits
        # a visible event)
        txs = self.scan_list_personal_txs(url=network.connection_url(), address = account_usr1.address,
                                          offset=0, size=20, show_public=False, show_synthetic=False)
        tx_hashes = [x['blockHash'] for x in txs['Receipts']]
        self.log.info('Returned block and tx hashes are;')
        for tx in txs['Receipts']: self.log.info('  %s %s' % (tx['blockHash'], tx['transactionHash']))

        self.assertTrue(txs is not None, abortOnError=True, assertMessage='Returned list is not None')
        self.assertTrue(len(tx_hashes) == 5, assertMessage='There should be five txs')
        self.assertTrue(tx_receipt1.blockHash.hex() in tx_hashes, assertMessage='Transaction tx1 should be returned')
        self.assertTrue(tx_receipt2.blockHash.hex() in tx_hashes, assertMessage='Transaction tx2 should be returned')
        self.assertTrue(tx_receipt3.blockHash.hex() in tx_hashes, assertMessage='Transaction tx3 should be returned')
        self.assertTrue(tx_receipt4.blockHash.hex() in tx_hashes, assertMessage='Transaction tx4 should be returned')

        # log out the transaction block hashes and tx hashes from requesting the list of personal transactions,
        # including the synthetic ones (these are the zen tokens that accrue for each transaction made)
        if False: # for now it is not supported to include public and synthetic transactions
            txs = self.scan_list_personal_txs(url=network.connection_url(), address = account_usr1.address,
                                              offset=0, size=20, show_public=False, show_synthetic=True)
            tx_hashes = [x['transactionHash'] for x in txs['Receipts']]
            self.log.info('Returned block and tx hashes are;')
            for tx in txs['Receipts']: self.log.info('  %s %s' % (tx['blockHash'], tx['transactionHash']))

            self.assertTrue(len(tx_hashes) == 8, assertMessage='There should be eight txs including synthetic')

