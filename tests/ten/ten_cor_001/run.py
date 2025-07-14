from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # get the network, and deploy the contracts
        network = self.get_network_connection()
        web3_deploy, account_deploy = network.connect_account1(self)
        storage = Storage(self, web3_deploy, 0)
        storage.deploy(network, account_deploy)

        # connect as an ephemeral test user and transact against the contracts
        self.log.info('')
        self.log.info('Create the ephemeral user 1 and fund them')
        pk = self.get_ephemeral_pk()
        web_usr1, account_usr1 = network.connect(self, private_key=pk, check_funds=True)

        self.log.info('')
        self.log.info('User 1 performs three contract calls')
        network.transact(self, web_usr1, storage.contract.functions.store(1), account_usr1, storage.GAS_LIMIT)
        network.transact(self, web_usr1, storage.contract.functions.store(2), account_usr1, storage.GAS_LIMIT)
