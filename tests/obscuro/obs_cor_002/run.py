from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):
    ONE_TOKEN =   1000000000000000000
    TEN_MINUS_1 = 100000000000000000
    TEN_MINUS_2 = 10000000000000000
    TEN_MINUS_3 = 1000000000000000
    TEN_MINUS_4 = 100000000000000

    def execute(self):
        # connect to the L2 network
        network = Obscuro

        web3_faucet, faucet_account = network.connect(Properties().faucet_pk(self.env), network.HOST, network.PORT)
        web3_user, user_account = network.connect_account1()

        faucet_obx_balance_before = web3_faucet.eth.get_balance(faucet_account.address)
        user_obx_balance_before = web3_user.eth.get_balance(user_account.address)
        self.log.info('Using account %s' % user_account.address)
        self.log.info('  L2 balances before;')
        self.log.info('    OBX Faucet balance = %d ' % faucet_obx_balance_before)
        self.log.info('    OBX User balance   = %d ' % user_obx_balance_before)

        tx = {
            'nonce': web3_faucet.eth.get_transaction_count(faucet_account.address),
            'to': user_account.address,
            'value': self.TEN_MINUS_1,
            'gas': 4*720000,
            'gasPrice':  web3_faucet.eth.gas_price
        }
        tx_sign = faucet_account.sign_transaction(tx)
        tx_hash = network.send_transaction(self, web3_faucet, None, tx_sign)
        tx_recp = network.wait_for_transaction(self, web3_faucet, tx_hash)

        faucet_obx_balance_after = web3_faucet.eth.get_balance(faucet_account.address)
        user_obx_balance_after = web3_user.eth.get_balance(user_account.address)
        self.log.info('  L2 balances after;')
        self.log.info('    OBX Faucet balance = %d ' % faucet_obx_balance_after)
        self.log.info('    OBX User balance   = %d ' % user_obx_balance_after)

        self.assertTrue(faucet_obx_balance_before - faucet_obx_balance_after == self.TEN_MINUS_1)
        self.assertTrue(user_obx_balance_after - user_obx_balance_before == self.TEN_MINUS_1)
