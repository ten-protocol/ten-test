import getpass, configparser
from pysys.constants import *
from pysys.exceptions import FileNotFoundException


class Properties:
    """Used as a holding class for properties."""

    def __init__(self):
        self.default_config = configparser.ConfigParser()
        self.default_config.read(filenames=os.path.join(PROJECT.root, '.default.properties'))

        self.user_config = configparser.ConfigParser()
        file = os.path.join(PROJECT.root, '.'+getpass.getuser()+'.properties')
        if os.path.exists(file):
            self.user_config.read(filenames=file)

    def get(self, section, option):
        if self.user_config.has_option(section, option):
            return self.user_config.get(section, option)
        else:
            return self.default_config.get(section, option)

    # binaries
    def solc_binary(self):
        path = self.get('binaries.%s' % PLATFORM, 'solc')
        if not os.path.exists(path):
            raise FileNotFoundException('Solc binary not found at default location %s' % path)
        return path

    def node_binary(self):
        path = self.get('binaries.%s' % PLATFORM, 'node')
        if not os.path.exists(path):
            raise FileNotFoundException('Node binary not found at default location %s' % path)
        return path

    def ganache_binary(self):
        path = self.get('binaries.%s' % PLATFORM, 'ganache')
        if not os.path.exists(path):
            raise FileNotFoundException('Ganache binary not found at default location %s' % path)
        return path

    # common to all environments
    def block_time_secs(self, key):
        return self.get('env.'+key, 'BlockTimeSecs')

    def account1pk(self):
        return self.get('env.all', 'Account1PK')

    def account2pk(self):
        return self.get('env.all', 'Account2PK')

    def account3pk(self):
        return self.get('env.all', 'Account3PK')

    def account4pk(self):
        return self.get('env.all', 'Account4PK')

    # obscuro specific properties
    def node_host(self, key):
        return self.get('env.'+key, 'NodeHost')

    def node_port_http(self, key):
        return self.get('env.'+key, 'NodePortHTTP')

    def node_port_ws(self, key):
        return self.get('env.'+key, 'NodePortWS')

    def faucet_url(self, key):
        return self.get('env.'+key, 'FaucetURL')

    def management_bridge_address(self, key):
        return self.get('env.'+key, 'ManagementBridgeAddress')

    def distro_account_pk(self, key):
        return self.get('env.'+key, 'DistroAccountPK')

    def l1_funded_account_pk(self, key):
        return self.get('env.'+key, 'L1FundedAccountPK')

    def l1_hoc_token_address(self, key):
        return self.get('env.'+key, 'L1TokenHOCContractAddress')

    def l1_poc_token_address(self, key):
        return self.get('env.'+key, 'L1TokenPOCContractAddress')

    def l2_funded_account_pk(self, key):
        return self.get('env.'+key, 'L2FundedAccountPK')

    def l2_hoc_token_address(self, key):
        return self.get('env.'+key, 'L2TokenHOCContractAddress')

    def l2_poc_token_address(self, key):
        return self.get('env.'+key, 'L2TokenPOCContractAddress')

    # infura related
    def infuraProjectID(self):
        return self.get('env.goerli', 'ProjectID')
