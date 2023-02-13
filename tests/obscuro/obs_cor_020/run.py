from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.erc20.minted_erc20 import MintedERC20Token
from obscuro.test.utils.bridge import BridgeUser
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):
    NAME = 'SmartyCoin'
    SYMB = 'SCN'

    def execute(self):
        props = Properties()

        # create the users for the test
        funded = BridgeUser(self, props.l1_funded_account_pk(self.env), props.l2_funded_account_pk(self.env))
        accnt1 = BridgeUser(self, props.account1pk(), props.account1pk())

        # deploy the ERC20 token and set the L1 contract instance
        self.log.info('Deploy the ERC20 token on the L1')
        token = MintedERC20Token(self, funded.l1.web3, self.NAME, self.SYMB, 10000)
        token.deploy(funded.l1.network, funded.l1.account, persist_nonce=False)

        funded.l1.add_token_contract(token.address, self.NAME, self.SYMB)
        accnt1.l1.add_token_contract(token.address, self.NAME, self.SYMB)

        # transfer tokens from the funded account to account1, account1 approves the bridge to transfer
        self.log.info('Transfer and approve tokens')
        funded.l1.transfer_token(self.SYMB, accnt1.l1.account.address, 200)
        accnt1.l1.approve_token(self.SYMB, accnt1.l1.bridge.address, 100)

        # whitelist the token, wait for it to be verified as finalised on L2
        self.log.info('Whitelist the token')
        _, xchain_msg = funded.l1.white_list_token(self.SYMB)
        accnt1.l2.wait_for_message(xchain_msg)

        # relay the whitelisting message and set the L2 contract instance
        self.log.info('Relay the token on L2')
        _, l2_token_address = accnt1.l2.relay_whitelist_message(xchain_msg)

        funded.l2.set_token_contract(l2_token_address, self.NAME, self.SYMB)
        accnt1.l2.set_token_contract(l2_token_address, self.NAME, self.SYMB)

        # send tokens across the bridge, and wait for it to be verified as finalised on L2, and then relay
        self.log.info('Send tokens on the L1 to cross the bridge')
        _, xchain_msg = accnt1.l1.send_erc20(self.SYMB, accnt1.l2.account.address, 10)
        accnt1.l2.wait_for_message(xchain_msg)

        self.log.info('Relay the send tokens request')
        _ = accnt1.l2.relay_message(xchain_msg)

        # print out the balances and perform test validation
        self.log.info('Print out token balances')
        balance_l1 = accnt1.l1.balance_for_token(self.SYMB)
        balance_l2 = accnt1.l2.balance_for_token(self.SYMB)
        self.log.info('    Account1 ERC20 balance L1 = %d ' % balance_l1)
        self.log.info('    Account1 ERC20 balance L2 = %d ' % balance_l2)
        self.assertTrue(balance_l1 == 190)
        self.assertTrue(balance_l2 == 10)



