import json, requests, os
from pysys.constants import PROJECT
from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.utils.properties import Properties


class ObscuroAdmin(ObscuroTest):
    """Test class used for pre-admin setup of an Obscuro network before running a set of tests.

    The ObscuroAdmin test class funds a network ready for use by the testcases. This includes natively funding the
    layer 1 with ETH, and bridging ERC20 tokens from the layer 1 to the layer 2. It also then includes distributing
    native OBX and the ERC20 tokens in layer 2 to the test users. 

    """
    ONE_GIGA = 1000000000000000000

    def fund_obx(self, network, web3_user, account_user, amount):
        """Fund OBX in the L2 to a users account, either through the faucet server or direct from the account."""
        if self.env in ['obscuro', 'obscuro.dev']:
            self.__obx_from_faucet_server(web3_user, account_user)
        else:
            self.__obx_from_funded_pk(network, web3_user, account_user, amount)

    def fund_obx_for_address_only(self, address):
        """Fund OBX for an account using the faucet server when only the address is known. """
        self.log.info('Increasing native OBX via the faucet server')
        headers = {'Content-Type': 'application/json'}
        data = {"address": address}
        requests.post(Properties().faucet_url(self.env), data=json.dumps(data), headers=headers)

    def transfer_token(self, network, token_name, token_address, web3_from, account_from, address, amount):
        """Transfer an ERC20 token amount from a recipient account to an address. """
        self.log.info('Running for token %s' % token_name)

        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as f:
            token = web3_from.eth.contract(address=token_address, abi=json.load(f))

        balance = token.functions.balanceOf(account_from.address).call()
        self.log.info('Sender token balance before = %d ' % balance)

        # transfer tokens from the funded account to the distro account
        network.transact(self, web3_from, token.functions.transfer(address, amount), account_from, 7200000)

        balance = token.functions.balanceOf(account_from.address).call()
        self.log.info('Sender token balance after = %d ' % balance)

    def print_token_balance(self, token_name, token_address, web3, account):
        """Print an ERC20 token balance of a recipient account. """
        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as f:
            token = web3.eth.contract(address=token_address, abi=json.load(f))

        balance = token.functions.balanceOf(account.address).call()
        self.log.info('Token balance for %s = %d ' % (token_name, balance))

    def __obx_from_faucet_server(self, web3_user, account_user):
        """Allocates native OBX to a users account from the faucet server."""
        self.log.info('Running for native OBX token using faucet server')
        user_obx = web3_user.eth.get_balance(account_user.address)
        self.log.info('L2 balances before;')
        self.log.info('  OBX User balance   = %d ' % user_obx)

        self.log.info('Running request on %s' % Properties().faucet_url(self.env))
        self.log.info('Running for user address %s' % account_user.address)
        headers = {'Content-Type': 'application/json'}
        data = {"address": account_user.address}
        requests.post(Properties().faucet_url(self.env), data=json.dumps(data), headers=headers)

        user_obx = web3_user.eth.get_balance(account_user.address)
        self.log.info('L2 balances after;')
        self.log.info('  OBX User balance   = %d ' % user_obx)

    def __obx_from_funded_pk(self, network, web3_user, account_user, amount):
        """Allocates native OBX to a users account from the pre-funded account."""
        self.log.info('Running for native OBX token using faucet pk')

        web3_funded, account_funded = network.connect(self, Properties().l2_funded_account_pk(self.env))
        funded_obx = web3_funded.eth.get_balance(account_funded.address)
        user_obx = web3_user.eth.get_balance(account_user.address)
        self.log.info('L2 balances before;')
        self.log.info('  OBX Funded balance = %d ' % funded_obx)
        self.log.info('  OBX User balance   = %d ' % user_obx)

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
            self.log.info('L2 balances after;')
            self.log.info('  OBX Funded balance = %d ' % funded_obx)
            self.log.info('  OBX User balance   = %d ' % user_obx)



