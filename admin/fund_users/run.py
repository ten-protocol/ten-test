import json, os, requests
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
        '0x87D64C4aF9A93c428a16C3a8E535767461D8451f',
        '0xFfB5982818055C507f606058d9073b2037937b9D',
        '0x02990c8683c9Bb0a9dC9DD19EbC1d1B9b38108A1',
        '0xcBfF76e15367db4Fa554085816A9eF4C54b44B5E',
        '0xae52EC7A8e98804a2731692b0f5717E086798363'
    ]
    USER = None

    def execute(self):
        network = Obscuro
        web3_deploy, deploy_account = network.connect(Properties().funded_deployment_account_pk(self.env), network.HOST, network.PORT)

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            hoc = web3_deploy.eth.contract(address=Properties().l2_hoc_token_address(self.env), abi=json.load(f))

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            poc = web3_deploy.eth.contract(address=Properties().l2_poc_token_address(self.env), abi=json.load(f))

        users = [self.USER] if self.USER is not None else self.REGISTERED_USERS
        for user_address in users:
            self.log.info('')
            self.log.info('Running for address %s' % user_address)
            self._obx(user_address)
            self._token(network, 'HOC', hoc, user_address, web3_deploy, deploy_account)
            self._token(network, 'POC', poc, user_address, web3_deploy, deploy_account)

    def _obx(self, user_address):
        """Increase native OBX on the layer 2."""
        self.log.info('Increasing native OBX via the faucet server')
        headers = {'Content-Type': 'application/json'}
        data = {"address": user_address}
        requests.post(Properties().faucet_url(self.env), data=json.dumps(data), headers=headers)

    def _token(self, network, token_name, token, user_address, web3_deploy, deploy_account):
        """Increase token on the layer 2."""
        self.log.info('Increasing ERC20 token for %s by %d ' % (token_name, self.TOKEN_TARGET))
        network.transact(self, web3_deploy, token.functions.transfer(user_address, self.TOKEN_TARGET), deploy_account, 7200000)
