from ten.test.basetest import TenNetworkTest
from ten.test.contracts.erc20 import ERC20Token
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        funded = BridgeUser(self, props.l1_funded_account_pk(self.env), props.account2pk(), 'funded')
        accnt1 = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')

        self.whitelist(funded, accnt1, 'USDC', props.l1_usdc_contract_address(self.env))
        self.whitelist(funded, accnt1, 'USDT', props.l1_usdt_contract_address(self.env))

    def whitelist(self, funded, accnt1, name, address):
        self.log.info('Whitelist and relaying %s token' %name)
        token = ERC20Token(self, funded.l1.web3, name, name, address)
        funded.l1.add_token_contract(token.address, name, name)
        accnt1.l1.add_token_contract(token.address, name, name)

        _, xchain_msg = accnt1.l1.white_list_token(name)
        accnt1.l2.wait_for_message(xchain_msg)
        _, l2_token_address = accnt1.l2.relay_whitelist_message(xchain_msg)
        self.log.info('The L2 token address for %s is %s' % (name, l2_token_address))

