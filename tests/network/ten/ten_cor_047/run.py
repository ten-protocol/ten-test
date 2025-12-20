from ten.test.basetest import TenNetworkTest
from ten.test.contracts.weth import WETH


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the create2 factory contract
        weth = WETH(self, web3)

        nonce = self.nonce_db.get_next_nonce(self, web3, account.address, self.env)
        target = weth.contract.functions.deposit
        params = {'nonce': nonce, 'gasPrice': web3.eth.gas_price, 'chainId': web3.eth.chain_id, 'value': web3.to_wei(0.01, 'ether') }
        estimate_gas = target.estimate_gas(params)
