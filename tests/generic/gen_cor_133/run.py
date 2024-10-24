import secrets
from web3 import Web3
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network and deploy the contract as on user
        network_1 = self.get_network_connection(name='deployer')
        web3_1, account_1 = network_1.connect_account1(self)
        storage_1 = Storage(self, web3_1, 100)
        storage_1.deploy(network_1, account_1)

        # try to transact as an other without any funds
        network_2 = self.get_network_connection(name='deployer')
        web3_2, account_2 = network_2.connect(self, private_key=secrets.token_hex(32), check_funds=False)
        storage_2 = Storage.clone(web3_2, account_2, storage_1)
        network_2.transact(self, web3_2, storage_2.contract.functions.store(1), account_2, storage_2.GAS_LIMIT,
                           estimate=True)
