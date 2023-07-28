import getpass, configparser
from pysys.constants import *
from pysys.exceptions import FileNotFoundException
from obscuro.test.utils.threading import thread_num


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

    def go_binary(self):
        path = self.get('binaries.%s' % PLATFORM, 'go')
        if not os.path.exists(path):
            raise FileNotFoundException('Go binary not found at default location %s' % path)
        return path

    def docker_binary(self):
        path = self.get('binaries.%s' % PLATFORM, 'docker')
        if not os.path.exists(path):
            raise FileNotFoundException('Docker binary not found at default location %s' % path)
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
            self.account1_3pk, self.account2_3pk, self.account3_3pk, self.account4_3pk,
            self.gg_appdev_pk, self.gg_endusr_pk
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

    # guessing game accounts
    def gg_appdev_pk(self): return self.get('env.all', 'GGAppDevPK')
    def gg_endusr_pk(self): return self.get('env.all', 'GGEndUsrPK')

    # accounts that can be used by additional nodes joining the network
    def extra_node_1pk(self): return self.get('env.all', 'ExtraNode1PK')

    # obscuro specific properties
    def node_host(self, key, node_host):
        if os.getenv('DOCKER_TEST_ENV'): return self.get('env.'+key, 'NodeHostDockerNetwork')
        if node_host is not None: return node_host
        return self.get('env.'+key, 'NodeHost')

    def node_port_http(self, key):
        return self.get('env.'+key, 'NodePortHTTP')

    def node_port_ws(self, key):
        return self.get('env.'+key, 'NodePortWS')

    def faucet_url(self, key):
        if os.getenv('DOCKER_TEST_ENV'): return self.get('env.'+key, 'FaucetURLDockerNetwork')
        return self.get('env.'+key, 'FaucetURL')

    def sequencer_id(self, key):
        return self.get('env.'+key, 'SequencerID')



    def l1_funded_account_pk(self, key):
        return self.get('env.'+key, 'L1FundedAccountPK')

    def l1_management_address(self, key):
        return self.get('env.'+key, 'L1ManagementAddress')

    def l1_bridge_address(self, key):
        return self.get('env.'+key, 'L1BridgeAddress')

    def l1_message_bus_address(self, key):
        return self.get('env.'+key, 'L1MessageBusAddress')

    def l1_cross_chain_messenger_address(self, key):
        return self.get('env.'+key, 'L1CrossChainMessengerAddress')

    def l1_start_block_hash(self, key):
        return self.get('env.'+key, 'L1StartBlockHash')

    def l2_bridge_address(self, key):
        return self.get('env.'+key, 'L2BridgeAddress')

    def l2_message_bus_address(self, key):
        return self.get('env.'+key, 'L2MessageBusAddress')

    def l2_cross_chain_messenger_address(self, key):
        return self.get('env.'+key, 'L2CrossChainMessengerAddress')

    # infura related
    def infuraProjectID(self):
        return self.get('env.goerli', 'ProjectID')

    # arbitrum related
    def abitrumAPIKey(self):
        return self.get('env.arbitrum', 'APIKey')