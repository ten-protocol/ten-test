from obscuro.test.basetest import ObscuroTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.obscuro import Obscuro


class PySysTest(ObscuroTest):
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
        '0xae52EC7A8e98804a2731692b0f5717E086798363',
        '0x84aeEf50078148BA3835F7a091df557145cA09bF',
        '0x49A56e979811228FE14af78A0De407f36A0F829C',
        '0xda76c50E43912fB5A764b966915c270B9a637487',
        '0x086071EcFcC6368113BC6b1acC4537953118f779',
        '0x7933bAed1643244ECa381C16521C0409AD364ca7',
        '0xB90a1e521587b1794ED09425C88F1d0fAa62Ab13',
        '0x743594c86D671F55A65129077F3B06a491bCf098',
        '0x5c755F5Fac7BC476918a83C0fbAf06c144148bf7'
    ]
    USER = None
    TOKENS = 50 * ObscuroTest.ONE_GIGA

    def execute(self):
        network = Obscuro
        web3_distro, account_distro = network.connect(self, Properties().distro_account_pk(self.env))
        hoc_address = Properties().l2_hoc_token_address(self.env)
        poc_address = Properties().l2_poc_token_address(self.env)

        users = [self.USER] if self.USER is not None else self.REGISTERED_USERS
        for user_address in users:
            self.log.info('')
            self.log.info('Running for address %s' % user_address)
            self.transfer_token(network, 'HOC', hoc_address, web3_distro, account_distro, user_address, self.TOKENS)
            self.transfer_token(network, 'POC', poc_address, web3_distro, account_distro, user_address, self.TOKENS)
