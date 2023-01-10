import threading
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        self.log.info('Thread: %s' % threading.currentThread().getName())

        # connect to the network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account3(self)
        self.log.info('Using account with address %s' % account.address)

        # get the balance
        balance = web3.eth.get_balance(account.address)
        self.log.info('Balance for account is %d' % balance)
        self.assertTrue(balance >= 0)

