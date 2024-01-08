import secrets, os
from web3 import Web3
from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):
    ITERATIONS = 10
    CLIENTS = 5

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)



