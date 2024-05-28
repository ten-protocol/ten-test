import secrets
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # get the network, and get or deploy the storage contract
        network = self.get_network_connection()
        web3_deploy, account_deploy = network.connect_account1(self)
        storage = Storage(self, web3_deploy, 0)
        storage.get_or_deploy(network, account_deploy)

        # connect as an ephemeral test user and transact agains the contract
        pk = secrets.token_hex(32)
        web3_usr, account_usr = network.connect(self, private_key=pk, check_funds=False)
        self.distribute_native(account_usr, network.ETH_ALLOC_EPHEMERAL)
        network.transact(self, web3_usr, storage.contract.functions.store(1), account_usr, storage.GAS_LIMIT)
        network.transact(self, web3_usr, storage.contract.functions.store(2), account_usr, storage.GAS_LIMIT)

        # list the personal transactions for the user
        txs = self.scan_list_personal_transactions(address = account_usr.address, offset=0, size=5)
        self.assertTrue(txs != None, abortOnError=True, assertMessage='Returned list is None')
        self.assertTrue(len(txs) == 2)