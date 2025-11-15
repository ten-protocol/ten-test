from ten.test.utils.properties import Properties
from ten.test.contracts.market import TestUSDC, TestTEN
from ten.test.dapps.market.markettest import MarketDappTest

class PySysTest(MarketDappTest):

    def execute(self):
        # get the chain id
        chain_id = self.web3_deployer.eth.chain_id
        self.log.info('Returned chain id is %d', chain_id)
        self.assertTrue(chain_id == self.network.chain_id())

        # check the erc20 contracts
        self.log.info('Test the TEN token exists and can be minted ...')
        self.check_token(self.web3_deployer, self.network, self.account_deploy, TestTEN(self, self.web3_deployer))
        self.log.info('Test the USDC token exists and can be minted ...')
        self.check_token(self.web3_deployer, self.network, self.account_deploy, TestUSDC(self, self.web3_deployer))

    def check_token(self, web3, network, account, token):
        self.log.info('Checking there is contract code at %s' % token.address)
        code = web3.eth.get_code(token.address)
        self.log.info("Contract bytecode length: %d", len(code))
        if code == b'' or code == '0x' or len(code) == 0:
            self.log.info("No contract code at that address — address wrong or contract not deployed.")
        else:
            balance_before = token.contract.functions.balanceOf(account.address).call()
            target = token.contract.functions.mint(account.address, 100)
            network.transact(self, web3, target, account, token.GAS_LIMIT, persist_nonce=False)
            balance_after = token.contract.functions.balanceOf(account.address).call()

            self.log.info('  Balance before = %d ', balance_before)
            self.log.info('  Balance after  = %d ', balance_after)
            self.assertTrue(balance_after-balance_before == 100, assertMessage='Balance delta should be 100')