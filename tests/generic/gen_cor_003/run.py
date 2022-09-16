from ethsys.basetest import EthereumTest
from ethsys.networks.factory import NetworkFactory


class PySysTest(EthereumTest):
    WEBSOCKET = False   # run with `pysys.py run -XWEBSOCKET` to enable

    def execute(self):
        # connect to the network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)
        self.log.info('Using account with address %s' % account.address)

        # get the balance
        balance = web3.eth.get_balance(account.address)
        self.log.info('Balance for new accounts is %d' % balance)
        self.assertTrue(balance >= 0)

