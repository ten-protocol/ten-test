from ten.test.basetest import TenNetworkTest
from ten.test.contracts.weth import WETH


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the create2 factory contract
        weth = WETH(self, web3)
        self.log.info('Contract address is %s' % weth.address)

        code = web3.eth.get_code(weth.address)
        self.log.info("Contract bytecode length: %d", len(code))
        if code == b'' or code == '0x' or len(code) == 0:
            self.log.info("No contract code at that address — address wrong or contract not deployed.")

