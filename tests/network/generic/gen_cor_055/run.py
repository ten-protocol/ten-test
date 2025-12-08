from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.error import DeleteMapping


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        contract = DeleteMapping(self, web3)
        contract.deploy(network, account)

        # set and get a user balance
        network.transact(self, web3, contract.contract.functions.setBalance(account.address, 20), account, contract.GAS_LIMIT)
        ret = int(contract.contract.functions.getBalance(account.address).call())
        self.log.info('Balance is %d' % ret)
        self.assertTrue(ret == 20, assertMessage='Expect balance to be 20')

        # delete and get a user balance
        network.transact(self, web3, contract.contract.functions.deleteBalance(account.address), account, contract.GAS_LIMIT)
        ret = int(contract.contract.functions.getBalance(account.address).call())
        self.log.info('Balance is %d' % ret)
        self.assertTrue(ret == 0, assertMessage='Expect balance to be 0')