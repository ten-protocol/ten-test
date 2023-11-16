from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        self.log.info('Using account with address %s', account.address)

        # get gas price
        gas_price = web3.eth.gas_price
        self.log.info('Gas price is %s', gas_price)
        self.assertTrue(gas_price >= 0)
