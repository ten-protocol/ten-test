from ten.test.basetest import TenNetworkTest
from ten.test.contracts.system import TransactionPostProcessor
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # get the network, deploy the storage contract
        network = self.get_network_connection()
        web3_deploy, account_deploy = network.connect_account1(self)
        storage = Storage(self, web3_deploy, 0)
        storage.deploy(network, account_deploy)

        # the reference to the transaction post processor
        processor = TransactionPostProcessor(self, web3_deploy)
        zen_address = processor.contract.functions.onBlockEndListeners(0).call()
        self.log.info('The zen address is %s' % zen_address)

        # connect as an ephemeral test user and transact against the storage contract
        pk = self.get_ephemeral_pk()
        web_usr1, account_usr1 = network.connect(self, private_key=pk, check_funds=True)
        network.transact(self, web_usr1, storage.contract.functions.store(1), account_usr1, storage.GAS_LIMIT)
        network.transact(self, web_usr1, storage.contract.functions.store(2), account_usr1, storage.GAS_LIMIT)
