from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.erc20.minted_erc20 import MintedERC20Token
from obscuro.test.utils.bridge import BridgeUser
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        props = Properties()

        # create the L1 and L2 connections, and users for the test
        funded = BridgeUser(self, props.l1_funded_account_pk(self.env), props.l2_funded_account_pk(self.env))
        accnt1 = BridgeUser(self, props.account1pk(), props.account1pk())

        # deploy the ERC20 token and set the L1 contract instance
        token = MintedERC20Token(self, funded.l1.web3, 'SmartyCoin', 'SCN', 10000)
        token.deploy(funded.l1.network, funded.l1.account, persist_nonce=False)

        funded.l1.set_token_from_address(token.contract_address)
        accnt1.l1.set_token_from_address(token.contract_address)

        # transfer tokens from the funded account to account1, and account1 approves the bridge to transfer
        funded.l1.transfer_token(accnt1.l1.account.address, 200)
        accnt1.l1.approve_token(accnt1.l1.bridge.contract_address, 100)

        # whitelist the token, wait for it to be verified as finalised on L2
        _, xchain_msg = funded.l1.white_list_token()
        funded.l2.wait_for_message(xchain_msg)

        # relay the whitelisting message and set the L2 contract instance
        _, l2_token_address = funded.l2.relay_whitelist_message(xchain_msg)
        
        funded.l2.set_token_from_address(l2_token_address)
        accnt1.l2.set_token_from_address(l2_token_address)

        # send tokens across the bridge, and wait for it to be verified as finalised on L2
        _, xchain_msg = accnt1.l1.token_send_erc20(accnt1.l2.account.address, 10)
        funded.l2.wait_for_message(xchain_msg)

        # print out the balances
        balance = accnt1.l1.token.functions.balanceOf(accnt1.l1.acount.address).call()
        self.log.info('  Account1 ERC20 balance L1 = %d ' % balance)
        balance = accnt1.l2.token.functions.balanceOf(accnt1.l2.account.address).call({"from":accnt1.l2.account.address})
        self.log.info('  Account1 ERC20 balance L2 = %d ' % balance)



