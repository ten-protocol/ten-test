from ten.test.basetest import TenNetworkTest
from ten.test.contracts.bridge import Management
from ten.test.contracts.bridge import L1CrossChainMessenger


class PySysTest(TenNetworkTest):

    def execute(self):
        network = self.get_l1_network_connection()
        web3, account = network.connect_account1(self)
        xchain = L1CrossChainMessenger(self, web3)
        management = Management(self, web3)

        xchain_msg = (account.address, 1, 1, 1, b'0x2bf58149a4eef36f0e402e31624a9bd4c4caf83c86d6c2c1d062b5d3b69199f0', 1)
        transf_msg = ['0xFeD8Fc00f96d652244c6EE628da65Ea766CcEc81', '0x22C844bDB44d29720aDbA4fc6d9B0eB0081f67f1', 4000000000000000, 36]
        proof = '0x0000000000000000000000000000000000000000000000000000000000000000'
        #proof = '0xd224583bd285127fa6617793392646fc3b4645df9d0c08813efd7d53af3b1562'
        root = '0xf6b270f94629d87b5518387efeb2ff341f7635172fce896f19cb9f0394d8c636'

        try:
            self.log.info('')
            self.log.info('xchain.contract.functions.relayMessageWithProof')
            network.transact(self, web3, xchain.contract.functions.relayMessageWithProof(xchain_msg, [proof], root),
                             account, gas_limit=xchain.GAS_LIMIT, persist_nonce=False)
        except Exception as e:
            self.log.error(e)

        try:
            self.log.info('')
            self.log.info('management.contract.functions.ExtractNativeValue')
            network.transact(self, web3, management.contract.functions.ExtractNativeValue(transf_msg, [proof], root),
                             account, gas_limit=management.GAS_LIMIT, persist_nonce=False)
        except Exception as e:
            self.log.error(e)







