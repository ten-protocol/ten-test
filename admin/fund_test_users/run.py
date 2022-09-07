import json, os, requests
from pysys.constants import PROJECT
from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):
    USERS = [
        Properties().account1pk(),
        Properties().account2pk(),
        Properties().account3pk(),
        Properties().gameuserpk()
    ]

    ONE_GIGA = 1000000000000000000
    OBX_TARGET = 1000 * ONE_GIGA
    OBX_THRESHOLD = 10 * ONE_GIGA

    TOKEN_TARGET = 50 * ONE_GIGA
    TOKEN_THRESHOLD = 5 * ONE_GIGA
    DISPLAY = False

    def execute(self):
        # connect to the L2 network
        network = Obscuro
        web3_deploy, deploy_account = network.connect(Properties().funded_deployment_account_pk(self.env), network.HOST,
                                                      network.PORT)
        web3_faucet, faucet_account = network.connect(Properties().faucet_pk(self.env), network.HOST,
                                                      network.ACCOUNT2_PORT)

        # get the contracts
        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            hoc_token = web3_deploy.eth.contract(address=Properties().l2_hoc_token_address(self.env), abi=json.load(f))

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            poc_token = web3_deploy.eth.contract(address=Properties().l2_poc_token_address(self.env), abi=json.load(f))

        # do the allocations
        for user in self.USERS:
            web3_user, user_account = network.connect(user, network.HOST, network.PORT)
            self.log.info('')
            self.log.info('Running for user address %s' % user_account.address)
            self.run_for_native_faucet_server(network, web3_user, user_account, web3_faucet, faucet_account)
            self.run_for_token(network, 'HOC', hoc_token, web3_user, user_account, web3_deploy, deploy_account,
                               web3_faucet, faucet_account)
            self.run_for_token(network, 'POC', poc_token, web3_user, user_account, web3_deploy, deploy_account,
                               web3_faucet, faucet_account)

    def run_for_native_faucet_server(self, network, web3_user, user_account, web3_faucet, faucet_account):
        """Allocates native OBX to a users account from the faucet server.

        This is a native transfer of funds via a transaction that targets a given users account address.
        """
        self.log.info('Running for native OBX token')
        faucet_obx = web3_faucet.eth.get_balance(faucet_account.address)
        user_obx = web3_user.eth.get_balance(user_account.address)
        self.log.info('  L2 balances before;')
        self.log.info('    OBX Faucet balance = %d ' % faucet_obx)
        self.log.info('    OBX User balance   = %d ' % user_obx)

        if not self.DISPLAY and user_obx < self.OBX_THRESHOLD:
            headers = {'Content-Type': 'application/json'}
            data = {"address": user_account.address}
            requests.post(Properties.faucet_url(self.env), data=json.dumps(data), headers=headers)

            faucet_obx = web3_faucet.eth.get_balance(faucet_account.address)
            user_obx = web3_user.eth.get_balance(user_account.address)
            self.log.info('  L2 balances after;')
            self.log.info('    OBX Faucet balance = %d ' % faucet_obx)
            self.log.info('    OBX User balance   = %d ' % user_obx)


    def run_for_native(self, network, web3_user, user_account, web3_faucet, faucet_account):
        """Allocates native OBX from the faucet to a users account.

        This is a native transfer of funds via a transaction that targets a given users account address.
        """
        self.log.info('Running for native OBX token')
        faucet_obx = web3_faucet.eth.get_balance(faucet_account.address)
        user_obx = web3_user.eth.get_balance(user_account.address)
        self.log.info('  L2 balances before;')
        self.log.info('    OBX Faucet balance = %d ' % faucet_obx)
        self.log.info('    OBX User balance   = %d ' % user_obx)

        if not self.DISPLAY and user_obx < self.OBX_THRESHOLD:
            amount = (self.OBX_TARGET - user_obx)
            self.log.info('Increase user account native OBX by %d ' % amount)
            tx = {
                'nonce': web3_faucet.eth.get_transaction_count(faucet_account.address),
                'to': user_account.address,
                'value': amount,
                'gas': 4 * 720000,
                'gasPrice': 21000
            }
            tx_sign = faucet_account.sign_transaction(tx)
            tx_hash = network.send_transaction(self, web3_faucet, None, tx_sign)
            network.wait_for_transaction(self, web3_faucet, tx_hash)

            faucet_obx = web3_faucet.eth.get_balance(faucet_account.address)
            user_obx = web3_user.eth.get_balance(user_account.address)
            self.log.info('  L2 balances after;')
            self.log.info('    OBX Faucet balance = %d ' % faucet_obx)
            self.log.info('    OBX User balance   = %d ' % user_obx)

    def run_for_token(self, network, token_name, token,
                      web3_user, user_account,
                      web3_deploy, deploy_account,
                      web3_faucet, faucet_account):
        """Allocates ERC20 tokens from a token contract to a users account within that contract.

        This is a reallocation of tokens within a token contract to a particular user.
        """
        self.log.info('Running for token %s' % token_name)

        deploy_balance = token.functions.balanceOf(deploy_account.address).call()
        user_balance = token.functions.balanceOf(user_account.address).call({'from': user_account.address})
        faucet_obx_balance = web3_faucet.eth.get_balance(faucet_account.address)
        deploy_obx_balance = web3_deploy.eth.get_balance(deploy_account.address)
        user_obx_balance = web3_user.eth.get_balance(user_account.address)
        self.log.info('  L2 balances before;')
        self.log.info('    OBX Faucet balance = %d ' % faucet_obx_balance)
        self.log.info('    OBX Deploy account balance = %d ' % deploy_obx_balance)
        self.log.info('    OBX User balance = %d ' % user_obx_balance)
        self.log.info('    %s Deploy account balance = %d ' % (token_name, deploy_balance))
        self.log.info('    %s User account balance = %d ' % (token_name, user_balance))

        if not self.DISPLAY and user_balance < self.TOKEN_THRESHOLD:
            amount = self.TOKEN_TARGET - user_balance
            self.log.info('Increase user account token %s by %d ' % (token_name, amount))

            network.transact(self, web3_deploy, token.functions.transfer(user_account.address, amount),
                             deploy_account, 7200000)

            deploy_balance = token.functions.balanceOf(deploy_account.address).call()
            user_balance = token.functions.balanceOf(user_account.address).call({'from': user_account.address})
            faucet_obx_balance = web3_faucet.eth.get_balance(faucet_account.address)
            deploy_obx_balance = web3_deploy.eth.get_balance(deploy_account.address)
            user_obx_balance = web3_user.eth.get_balance(user_account.address)
            self.log.info('  L2 balances after;')
            self.log.info('    OBX Faucet balance = %d ' % faucet_obx_balance)
            self.log.info('    OBX Deploy account balance = %d ' % deploy_obx_balance)
            self.log.info('    OBX User balance = %d ' % user_obx_balance)
            self.log.info('    %s Deploy account balance = %d ' % (token_name, deploy_balance))
            self.log.info('    %s User account balance = %d ' % (token_name, user_balance))
