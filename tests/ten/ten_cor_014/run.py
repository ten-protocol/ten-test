from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # get the network, and get or deploy the storage contract
        network = self.get_network_connection()
        web3_deploy, account_deploy = network.connect_account1(self)
        storage = Storage(self, web3_deploy, 0)
        storage.deploy(network, account_deploy)

        # connect as an ephemeral test user and transact agains the contract
        pk = self.get_ephemeral_pk()
        web3_usr, account_usr = network.connect(self, private_key=pk, check_funds=False)
        self.distribute_native(account_usr, network.ETH_ALLOC_EPHEMERAL)
        tx_receipt1 = network.transact(self, web3_usr, storage.contract.functions.store(1), account_usr, storage.GAS_LIMIT)
        tx_receipt2 = network.transact(self, web3_usr, storage.contract.functions.store(2), account_usr, storage.GAS_LIMIT)

        pk2 = self.get_ephemeral_pk()
        web3_usr2, account_usr2 = network.connect(self, private_key=pk2, check_funds=True)
    
        # second user sends funds to our test user
        transfer_amount = web3_usr2.to_wei(0.001, 'ether')
        tx = {'to': account_usr.address,'value': transfer_amount,'gasPrice': web3_usr2.eth.gas_price}
        tx['gas'] = web3_usr2.eth.estimate_gas(tx)
        tx_receipt3 = network.tx(self, web3_usr2, tx, account_usr2, verbose=True, txstr='transfer to test user')

        # list the personal transactions for the user
        txs = self.scan_list_personal_transactions(url=network.connection_url(), address = account_usr.address, offset=0, size=5)
        tx_hashs = [x['blockHash'] for x in txs['Receipts']]
        self.assertTrue(txs != None, abortOnError=True, assertMessage='Returned list is None')
        self.assertTrue(len(txs) == 3)
        self.assertTrue(tx_receipt1.blockHash.hex() in tx_hashs)
        self.assertTrue(tx_receipt2.blockHash.hex() in tx_hashs)
        self.assertTrue(tx_receipt3.blockHash.hex() in tx_hashs)
