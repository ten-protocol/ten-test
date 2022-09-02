import json, os
from pysys.constants import PROJECT
from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):
    REGISTERED_USERS = [
        '0x686Ad719004590e98F182feA3516d443780C64a1',
        '0x85E1Cc949Bca27912e3e951ad1F68afD1cc4aB15',
        '0x7719A2b2BeC6a98508975C168A565FffCF9Dc266',
        '0xD993601a218fB40147328ac8BCF086Dcc6eb3867',
        '0x6Bd7B418C4f4e944571F8EE4D7DBD5E44279d579',
        '0xa2aE6f0B2E8CC472c66905622ba244E58cB9813D',
        '0x424706Da31E53a4859e560DB7ed908d6534973C0',
        '0x61f991693aee28dbF4B7CBBB0ACf53ea92F219a3',
        '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
        '0xFfB5982818055C507f606058d9073b2037937b9D',
        '0x7AFcBAC69f6339e29FCe40759FFBFb25F0CCe314',
        '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
        '0xe21B920811B0C859834aa402f3F676012F1d6759',
        '0xF66FB3790A8A4B9bEF60f27D0f56cc7b3ADEE992',
        '0x87D64C4aF9A93c428a16C3a8E535767461D8451f'
    ]

    ONE_GIGA = 1000000000000000000
    OBX_TARGET = 50 * ONE_GIGA
    TOKEN_TARGET = 50 
    USER = None

    def execute(self):
        # connect to the L2 network
        network = Obscuro
        web3_deploy, deploy_account = network.connect(Properties().funded_deployment_account_pk(self.env), network.HOST, network.PORT)
        web3_faucet, faucet_account = network.connect(Properties().faucet_pk(self.env), network.HOST, network.ACCOUNT2_PORT)

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            hoc_token = web3_deploy.eth.contract(address=Properties().l2_hoc_token_address(self.env), abi=json.load(f))

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            poc_token = web3_deploy.eth.contract(address=Properties().l2_poc_token_address(self.env), abi=json.load(f))

        if self.USER is None: users = self.REGISTERED_USERS
        else: users = [self.USER]

        for user_address in users:
            self.log.info('')
            self.log.info('Running for address %s' % user_address)
            self.run_for_native(network, user_address, web3_faucet, faucet_account, self.OBX_TARGET)
            self.run_for_token(network, user_address, 'HOC', hoc_token, web3_deploy, deploy_account)
            self.run_for_token(network, user_address, 'POC', poc_token, web3_deploy, deploy_account)

    def run_for_native(self, network, user_address, web3_faucet, faucet_account, amount):
        """Allocates native OBX from the faucet to a users account."""
        self.log.info('Running for native OBX token')
        self.log.info('  Native OBX balance before;')
        self.log.info('    Faucet balance = %d ' % web3_faucet.eth.get_balance(faucet_account.address))

        tx = {
            'nonce': web3_faucet.eth.get_transaction_count(faucet_account.address),
            'to': user_address,
            'value': amount,
            'gas': 4 * 720000,
            'gasPrice': 21000
        }
        tx_sign = faucet_account.sign_transaction(tx)
        tx_hash = network.send_transaction(self, web3_faucet, None, tx_sign)
        network.wait_for_transaction(self, web3_faucet, tx_hash)

        self.log.info('  Native OBX balance after;')
        self.log.info('    Faucet balance = %d ' % web3_faucet.eth.get_balance(faucet_account.address))

    def run_for_token(self, network, user_address, token_name, token,
                      web3_deploy, deploy_account):
        """Allocates ERC20 tokens from the token contract to a users account within that contract."""
        self.log.info('Running for token %s' % token_name)

        # balance before transaction
        deploy_balance = token.functions.balanceOf(deploy_account.address).call()
        self.log.info('  Token balance before;')
        self.log.info('    Deploy balance = %d ' % deploy_balance)

        # transfer funds from the deployment address to the user account
        network.transact(self, web3_deploy, token.functions.transfer(user_address, self.TOKEN_TARGET), deploy_account, 7200000)

        # balance after transaction
        deploy_balance = token.functions.balanceOf(deploy_account.address).call()
        self.log.info('  Token balance after;')
        self.log.info('    Deploy balance = %d ' % deploy_balance)