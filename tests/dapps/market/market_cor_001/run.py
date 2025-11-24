from ten.test.basetest import TenNetworkTest
from ten.test.dapps.market.admin import MarketDappAdmin


class PySysTest(TenNetworkTest):

    def execute(self):
        # the actors in the test
        admin = MarketDappAdmin(self)

        # get the chain id
        chain_id = admin.web3.eth.chain_id
        self.log.info('Returned chain id is %d', chain_id)
        self.assertTrue(chain_id == admin.network.chain_id())

        # check the erc20 contracts
        self.log.info('Test the TEN token exists and can be minted ...')
        self.check_token(admin, admin.ten)
        self.log.info('Test the USDC token exists and can be minted ...')
        self.check_token(admin, admin.usdc)

    def check_token(self, admin, token):
        self.log.info('Checking there is contract code at %s' % token.address)
        code = admin.web3.eth.get_code(token.address)
        self.log.info("Contract bytecode length: %d", len(code))
        if code == b'' or code == '0x' or len(code) == 0:
            self.log.info("No contract code at that address — address wrong or contract not deployed.")
        else:
            balance_before = token.contract.functions.balanceOf(admin.address).call()
            target = token.contract.functions.mint(admin.address, 100)
            admin.network.transact(self, admin.web3, target, admin.account, token.GAS_LIMIT, persist_nonce=False)
            balance_after = token.contract.functions.balanceOf(admin.address).call()

            self.log.info('  Balance before = %d ', balance_before)
            self.log.info('  Balance after  = %d ', balance_after)
            self.assertTrue(balance_after-balance_before == 100, assertMessage='Balance delta should be 100')