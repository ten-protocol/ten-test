import getpass, configparser
from pathlib import Path
from pysys.constants import *
from pysys.exceptions import FileNotFoundException
from ten.test.utils.threading import thread_num


class Properties:
    """Used as a holding class for properties."""
    L1ManagementAddress = None
    L1BridgeAddress = None
    L1MessageBusAddress = None
    L1CrossChainMessengerAddress = None
    L2BridgeAddress = None
    L2MessageBusAddress = None
    L2CrossChainMessengerAddress = None

    def __init__(self):
        self.default_config = configparser.ConfigParser()
        self.default_config.read(filenames=os.path.join(PROJECT.root, '.default.properties'))

        self.user_config = configparser.ConfigParser()
        file1 = os.path.join(Path.home(), '.tentest', 'user.properties')
        file2 = os.path.join(PROJECT.root, '.'+getpass.getuser()+'.properties')
        if os.path.exists(file1):
            self.user_config.read(filenames=file1)
        elif os.path.exists(file2):
            # @TODO remove support for this in the future in preference to the user.properties
            self.user_config.read(filenames=file2)

    def get(self, section, option):
        if self.user_config.has_option(section, option):
            return self.user_config.get(section, option)
        elif self.default_config.has_option(section, option):
            return self.default_config.get(section, option)
        else:
            return None

    # binaries
    def solc_binary(self):
        path = self.get('binaries.%s' % PLATFORM, 'solc')
        if not os.path.exists(path):
            raise FileNotFoundException('Solc binary not found at default location %s' % path)
        return path

    def ganache_binary(self):
        path = self.get('binaries.%s' % PLATFORM, 'ganache')
        if not os.path.exists(path):
            raise FileNotFoundException('Ganache binary not found at default location %s' % path)
        return path

    def gnuplot_binary(self):
        path = self.get('binaries.%s' % PLATFORM, 'gnuplot')
        if not os.path.exists(path):
            raise FileNotFoundException('Gnuplot binary not found at default location %s' % path)
        return path

    def node_binary(self):
        path = self.get('binaries.%s' % PLATFORM, 'node')
        if not os.path.exists(path):
            raise FileNotFoundException('Node binary not found at default location %s' % path)
        return path

    def node_path(self):
        return self.get('binaries.%s' % PLATFORM, 'node_path')

    def npm_binary(self):
        path = self.get('binaries.%s' % PLATFORM, 'npm')
        if not os.path.exists(path):
            raise FileNotFoundException('npm binary not found at default location %s' % path)
        return path

    def npx_binary(self):
        path = self.get('binaries.%s' % PLATFORM, 'npx')
        if not os.path.exists(path):
            raise FileNotFoundException('npx binary not found at default location %s' % path)
        return path

    # common to all environments
    def block_time_secs(self, key):
        return self.get('env.'+key, 'BlockTimeSecs')

    # all accounts on the network layer that may hold funds
    def accounts(self):
        return [
            self.fundacntpk,
            self.account1_1pk, self.account2_1pk, self.account3_1pk, self.account4_1pk,
            self.account2_2pk, self.account2_2pk, self.account3_2pk, self.account4_2pk,
            self.account1_3pk, self.account2_3pk, self.account3_3pk, self.account4_3pk
        ]

    def fundacntpk(self): return self.get('env.all', 'FundAcntPK')
    def account1pk(self): return getattr(self, "account1_%dpk" % thread_num())()
    def account2pk(self): return getattr(self, "account2_%dpk" % thread_num())()
    def account3pk(self): return getattr(self, "account3_%dpk" % thread_num())()
    def account4pk(self): return getattr(self, "account4_%dpk" % thread_num())()

    # accounts 1 to 4 used by thread-1 or the main thread
    def account1_1pk(self): return self.get('env.all', 'Account1PK')
    def account2_1pk(self): return self.get('env.all', 'Account2PK')
    def account3_1pk(self): return self.get('env.all', 'Account3PK')
    def account4_1pk(self): return self.get('env.all', 'Account4PK')

    # accounts 1 to 4 used by thread-2
    def account1_2pk(self): return self.get('env.all', 'Account5PK')
    def account2_2pk(self): return self.get('env.all', 'Account6PK')
    def account3_2pk(self): return self.get('env.all', 'Account7PK')
    def account4_2pk(self): return self.get('env.all', 'Account8PK')

    # accounts 1 to 4 used by thread-3
    def account1_3pk(self): return self.get('env.all', 'Account9PK')
    def account2_3pk(self): return self.get('env.all', 'Account10PK')
    def account3_3pk(self): return self.get('env.all', 'Account11PK')
    def account4_3pk(self): return self.get('env.all', 'Account12PK')

    # node addresses
    def sequencer_address(self, key): return self.get('env.'+key, 'SequencerAddress')
    def validator1_address(self, key): return self.get('env.' + key, 'Validator1Address')
    def validator2_address(self, key): return self.get('env.' + key, 'Validator2Address')

    # L1 deployment address
    def l1_deployer_address(self, key): return self.get('env.'+key, 'L1DeployerAddress')

    # network connection properties
    def host_http(self, key):
        if os.getenv('DOCKER_TEST_ENV'): return self.get('env.'+key, 'HostHTTPDockerNetwork')
        return self.get('env.'+key, 'HostHTTP')

    def host_ws(self, key):
        if os.getenv('DOCKER_TEST_ENV'): return self.get('env.'+key, 'HostWSDockerNetwork')
        return self.get('env.'+key, 'HostWS')

    def port_http(self, key): return int(self.get('env.'+key, 'PortHTTP'))
    def port_ws(self, key): return int(self.get('env.'+key, 'PortWS'))
    def chain_id(self, key): return int(self.get('env.'+key, 'ChainID'))

    # ten specific properties
    def node_host(self, key, node_host):
        if os.getenv('DOCKER_TEST_ENV'): return self.get('env.'+key, 'NodeHostDockerNetwork')
        if node_host is not None: return node_host
        return self.get('env.'+key, 'L2NodeHost')

    def l1_host_http(self, key):
        return self.get('env.'+key, 'L1NodeHostHTTP')

    def l1_host_ws(self, key):
        return self.get('env.'+key, 'L1NodeHostWS')

    def l1_port_http(self, key):
        return int(self.get('env.'+key, 'L1NodePortHTTP'))

    def l1_port_ws(self, key):
        return int(self.get('env.'+key, 'L1NodePortWS'))

    def node_port_http(self, key):
        return int(self.get('env.'+key, 'L2NodePortHTTP'))

    def node_port_ws(self, key):
        return int(self.get('env.'+key, 'L2NodePortWS'))

    def faucet_url(self, key):
        if os.getenv('DOCKER_TEST_ENV'): return self.get('env.'+key, 'FaucetURLDockerNetwork')
        return self.get('env.'+key, 'FaucetURL')

    def l1_funded_account_pk(self, key):
        return self.get('env.'+key, 'L1FundedAccountPK')

    def l1_management_address(self):
        return self.L1ManagementAddress

    def l1_bridge_address(self):
        return self.L1BridgeAddress

    def l1_message_bus_address(self):
        return self.L1MessageBusAddress

    def l1_cross_chain_messenger_address(self):
        return self.L1CrossChainMessengerAddress

    def l2_bridge_address(self):
        return self.L2BridgeAddress

    def l2_message_bus_address(self):
        return self.L2MessageBusAddress

    def l2_cross_chain_messenger_address(self):
        return self.L2CrossChainMessengerAddress

    def l2_gas_payment_account_pk(self, key):
        return self.get('env.'+key, 'L2GasPaymentAccountPK')

    # infura related
    def infuraProjectID(self):
        return self.get('env.goerli', 'ProjectID')

    # arbitrum related
    def arbitrumSepoliaAPIKey(self):
        return self.get('env.arbitrum.sepolia', 'APIKey')

    # sepolia related
    def sepoliaAPIKey(self):
        return self.get('env.sepolia', 'APIKey')