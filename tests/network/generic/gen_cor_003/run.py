from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account3(self)
        self.log.info('Using account with address %s', account.address)

        # get the balance
        balance = web3.eth.get_balance(account.address)
        self.log.info('Balance for account is %d', balance)
        self.assertTrue(balance >= 0)

