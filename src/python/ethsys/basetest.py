import json, requests
from pysys.basetest import BaseTest
from ethsys.utils.properties import Properties


class EthereumTest(BaseTest):
    ONE_GIGA = 1000000000000000000

    def __init__(self, descriptor, outsubdir, runner):
        """Call the parent constructor but set the mode to obscuro if non is set. """
        super().__init__(descriptor, outsubdir, runner)
        self.env = 'obscuro' if self.mode is None else self.mode

    def fund_obx(self, network, web3_user, account_user, amount):
        """Fund OBX in the L2 to a users account, either through the faucet server or direct from the account."""
        if self.env in ['obscuro', 'obscuro.dev']:
            self.obx_from_faucet_server(web3_user, account_user)
        else:
            self.obx_from_funded_pk(network, web3_user, account_user, amount)

    def obx_from_faucet_server(self, web3_user, account_user):
        """Allocates native OBX to a users account from the faucet server."""
        self.log.info('Running for native OBX token using faucet server')
        user_obx = web3_user.eth.get_balance(account_user.address)
        self.log.info('  L2 balances before;')
        self.log.info('    OBX User balance   = %d ' % user_obx)

        self.log.info('Running request on %s' % Properties().faucet_url(self.env))
        self.log.info('Running for user address %s' % account_user.address)
        headers = {'Content-Type': 'application/json'}
        data = {"address": account_user.address}
        requests.post(Properties().faucet_url(self.env), data=json.dumps(data), headers=headers)

        user_obx = web3_user.eth.get_balance(account_user.address)
        self.log.info('  L2 balances after;')
        self.log.info('    OBX User balance   = %d ' % user_obx)

    def obx_from_funded_pk(self, network, web3_user, account_user, amount):
        """Allocates native OBX to a users account from the pre-funded account."""
        self.log.info('Running for native OBX token using faucet pk')

        web3_funded, account_funded = network.connect(self, Properties().l2_funded_account_pk(self.env))
        funded_obx = web3_funded.eth.get_balance(account_funded.address)
        user_obx = web3_user.eth.get_balance(account_user.address)
        self.log.info('  L2 balances before;')
        self.log.info('    OBX Funded balance = %d ' % funded_obx)
        self.log.info('    OBX User balance   = %d ' % user_obx)

        if user_obx < amount:
            amount = amount - user_obx

            # transaction from the faucet to the deployment account
            tx = {
                'nonce': web3_funded.eth.get_transaction_count(account_funded.address),
                'to': account_user.address,
                'value': amount,
                'gas': 4 * 720000,
                'gasPrice': 21000
            }
            tx_sign = account_funded.sign_transaction(tx)
            tx_hash = network.send_transaction(self, web3_funded, tx_sign)
            network.wait_for_transaction(self, web3_funded, tx_hash)

            funded_obx = web3_funded.eth.get_balance(account_funded.address)
            user_obx = web3_user.eth.get_balance(account_user.address)
            self.log.info('  L2 balances after;')
            self.log.info('    OBX Funded balance = %d ' % funded_obx)
            self.log.info('    OBX User balance   = %d ' % user_obx)

