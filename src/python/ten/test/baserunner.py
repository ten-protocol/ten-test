import os, shutil, sys, json, requests, time, socket
from web3 import Web3
from collections import OrderedDict
from web3 import Web3
from pathlib import Path
from eth_account import Account
from eth_account.messages import encode_typed_data
from pysys.constants import PROJECT, BACKGROUND
from pysys.exceptions import AbortExecution
from pysys.constants import LOG_TRACEBACK
from pysys.utils.logutils import BaseLogFormatter
from ten.test.persistence.rates import RatesPersistence
from ten.test.persistence.nonce import NoncePersistence
from ten.test.persistence.counts import CountsPersistence
from ten.test.persistence.funds import FundsPersistence, PandLPersistence, GasPricePersistence
from ten.test.persistence.results import PerformanceResultsPersistence, TxCostResultsPersistence
from ten.test.persistence.contract import ContractPersistence
from ten.test.utils.properties import Properties
from ten.test.utils.cloud import is_cloud_vm


class TenRunnerPlugin():
    """Runner class for running a set of tests against a given environment.

    The runner is responsible for starting any applications prior to running the requested tests. When running
    against Ganache, a local Ganache will be started. All processes started by the runner are automatically stopped
    when the tests are complete. Note the runner should remain independent to the BaseTest, i.e. is stand alone as
    much as possible. This is because most of the framework is written to be test centric.
    """
    MSG_ID = 1                      # global used for http message requests numbers

    def __init__(self):
        """Constructor. """
        self.env = None
        self.NODE_HOST = None
        self.balances = OrderedDict()
        self.cloud_metadata = is_cloud_vm()
        self.is_cloud_vm = self.cloud_metadata is not None
        self.user_dir = os.path.join(str(Path.home()), '.tentest')
        if not os.path.exists(self.user_dir): os.makedirs(self.user_dir)

    def setup(self, runner):
        """Set up a runner plugin to start any processes required to execute the tests. """
        if runner.mode is None:
            runner.log.warn('A valid mode must be supplied')
            runner.log.info('Supported modes are; ')
            runner.log.info('   ten.sepolia   Ten sepolia testnet')
            runner.log.info('   ten.uat       Ten uat testnet')
            runner.log.info('   ten.dev       Ten dev testnet')
            runner.log.info('   ten.local     Ten local testnet')
            runner.log.info('   ten.sim       Ten sim testnet')
            runner.log.info('   arbitrum      Arbitrum Network')
            runner.log.info('   ganache       Ganache Network started by the framework')
            runner.log.info('   sepolia       Sepolia Network')
            sys.exit()

        self.env = runner.mode
        self.NODE_HOST = runner.getXArg('NODE_HOST', '')
        if self.NODE_HOST == '': self.NODE_HOST = None
        runner.output = os.path.join(PROJECT.root, '.runner')
        runner.log.info('Runner is executing against environment %s', self.env)

        # create dir for any runner output
        if os.path.exists(runner.output): shutil.rmtree(runner.output)
        os.makedirs(runner.output)

        # get the machine name
        if self.is_cloud_vm:
            self.machine_name = self.cloud_metadata['compute']['name']
            runner.log.info('Running on azure (%s, %s)' % (self.machine_name, self.cloud_metadata['compute']['location']))
        else:
            self.machine_name = socket.gethostname()
            runner.log.info('Running on local (%s)' % self.machine_name)

        # every test has its own connection to the dbs - use a remote mysql persistence layer if we are running in
        # azure, and it is not a local testnet. The exception for this is the nonce db where it is always local.
        use_remote = (not self.is_local_ten() and self.is_cloud_vm)
        rates_db = RatesPersistence.init(use_remote, self.user_dir, self.machine_name)
        nonce_db = NoncePersistence.init(use_remote, self.user_dir, self.machine_name)
        contracts_db = ContractPersistence.init(use_remote, self.user_dir, self.machine_name)
        funds_db = FundsPersistence.init(use_remote, self.user_dir, self.machine_name)
        pandl_db = PandLPersistence.init(use_remote, self.user_dir, self.machine_name)
        gas_db = GasPricePersistence.init(use_remote, self.user_dir, self.machine_name)
        counts_db = CountsPersistence.init(use_remote, self.user_dir, self.machine_name)
        results_db = PerformanceResultsPersistence.init(use_remote, self.user_dir, self.machine_name)
        txcosts_db = TxCostResultsPersistence.init(use_remote, self.user_dir, self.machine_name)

        eth_price = self.get_eth_price()
        if eth_price is not None:
            runner.log.info('Current ETH price is %f USD' % eth_price)
            rates_db.insert_rates('ETH', 'USD', int(time.time()), eth_price)
        else:
            _, eth_price = rates_db.get_latest_rate('ETH', 'USD')

        if self.is_ten() and runner.threads > 3:
            raise Exception('Max threads against Ten cannot be greater than 3')
        elif self.env == 'arbitrum.sepolia' and runner.threads > 1:
            raise Exception('Max threads against Arbitrum cannot be greater than 1')
        elif self.env == 'ganache' and runner.threads > 3:
            raise Exception('Max threads against Ganache cannot be greater than 3')
        elif self.env == 'sepolia' and runner.threads > 1:
            raise Exception('Max threads against Sepolia cannot be greater than 1')

        try:
            if self.is_ten():
                try:
                    runner.log.info('Getting and setting the Ten contract addresses')
                    self.__set_contract_addresses(runner)
                except:
                    runner.log.info('Error setting the Ten contract addresses')

                props = Properties()
                account = Web3().eth.account.from_key(props.fundacntpk())
                gateway_url = '%s:%d' % (props.host_http(self.env), props.port_http(self.env))
                runner.log.info('Joining network using url %s', '%s/v1/join/' % gateway_url)
                user_id = self.__join('%s/v1/join/' % gateway_url)
                runner.log.info('User id is %s', user_id)

                runner.log.info('Registering account %s with the network', account.address)
                response = self.__register(account, '%s/v1/authenticate/?token=%s' % (gateway_url, user_id), user_id)
                runner.log.info('Registration success was %s', response.ok)
                web3 = Web3(Web3.HTTPProvider('%s/v1/?token=%s' % (gateway_url, user_id)))
                runner.addCleanupFunction(lambda: self.__print_cost(runner,
                                                                    '%s/v1/authenticate/?token=%s' % (gateway_url, user_id),
                                                                    web3, user_id, eth_price))
                balance = web3.from_wei(web3.eth.get_balance(account.address), 'ether')

                if balance < 200 and Properties().l1_abstraction(self.env) == 'TenL1Geth':
                    runner.log.info('Funded key balance below threshold ... making faucet call')
                    self.fund_eth_from_faucet_server(runner)
                    self.fund_eth_from_faucet_server(runner)

                runner.log.info('')
                runner.log.info('Accounts with non-zero funds;')
                for fn in Properties().accounts():
                    account = web3.eth.account.from_key(fn())
                    self.__register(account, '%s/v1/authenticate/?token=%s' % (gateway_url, user_id), user_id)
                    self.balances[fn.__name__] = web3.from_wei(web3.eth.get_balance(account.address), 'ether')
                    if self.balances[fn.__name__] > 0:
                        runner.log.info("  Funds for %s: %.18f ETH", fn.__name__, self.balances[fn.__name__],
                                        extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))

                runner.log.info('')
                runner.log.info('Checking alignment of account nonce persistence;')
                for fn in Properties().accounts():
                    account = web3.eth.account.from_key(fn())
                    persisted = nonce_db.get_latest_nonce(account.address, self.env)
                    tx_count = web3.eth.get_transaction_count(account.address)
                    if (persisted is None) or (persisted != tx_count-1):
                        # persisted is the last persisted nonce, tx_count is the number of txs for this account
                        # as nonces started at zero, 1 tx count should mean last persisted was zero (one less)
                        runner.log.warn("  Resetting persistence for %s, persisted %s, count %d", fn.__name__,
                                        str(persisted), tx_count, extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
                        if (persisted is not None) and (persisted > tx_count-1): nonce_db.delete_from(account.address, self.env, tx_count)
                        nonce_db.insert(account.address, self.env, tx_count-1, 'RESET')
                runner.log.info('')

            elif self.env == 'ganache':
                nonce_db.delete_environment('ganache')
                hprocess = self.run_ganache(runner)
                runner.addCleanupFunction(lambda: self.__stop_process(hprocess))

        except Exception as e:
            runner.log.warn('Error executing runner plugin startup actions %s', e)
            runner.cleanup()

        rates_db.close()
        nonce_db.close()
        contracts_db.close()
        funds_db.close()
        pandl_db.close()
        gas_db.close()
        counts_db.close()
        results_db.close()
        txcosts_db.close()

    def run_ganache(self, runner):
        """Run ganache for use by the tests. """
        runner.log.info('Starting ganache server to run tests through managed instance')
        stdout = os.path.join(runner.output, 'ganache.out')
        stderr = os.path.join(runner.output, 'ganache.err')
        port = Properties().port_http(key='ganache')

        arguments = []
        arguments.extend(('--port', str(port)))
        arguments.extend(('--account', '0x%s,50000000000000000000' % Properties().fundacntpk()))
        arguments.extend(('--blockTime', Properties().block_time_secs(self.env)))
        hprocess = runner.startProcess(command=Properties().ganache_binary(), displayName='ganache',
                                       workingDir=runner.output, environs=os.environ, quiet=True,
                                       arguments=arguments, stdout=stdout, stderr=stderr, state=BACKGROUND)

        runner.waitForSignal(stdout, expr='Listening on 127.0.0.1:%d' % port, timeout=30)
        return hprocess

    def run_wallet(self, runner):
        """Run a single wallet extension for use by the tests. """
        runner.log.info('Starting wallet extension to run tests')
        port = runner.getNextAvailableTCPPort()
        stdout = os.path.join(runner.output, 'wallet.out')
        stderr = os.path.join(runner.output, 'wallet.err')

        props = Properties()
        arguments = []
        arguments.extend(('--nodeHost', Properties().node_host(self.env, self.NODE_HOST)))
        arguments.extend(('--nodePortHTTP', str(props.node_port_http(self.env))))
        arguments.extend(('--nodePortWS', str(props.node_port_ws(self.env))))
        arguments.extend(('--port', str(port)))
        arguments.extend(('--portWS', str(runner.getNextAvailableTCPPort())))
        arguments.extend(('--logPath', os.path.join(runner.output, 'wallet_logs.txt')))
        arguments.extend(('--databasePath', os.path.join(runner.output, 'wallet_database')))
        arguments.append('--verbose')
        hprocess = runner.startProcess(command=os.path.join(PROJECT.root, 'artifacts', 'wallet_extension', 'wallet_extension'),
                                       displayName='wallet_extension', workingDir=runner.output, environs=os.environ,
                                       quiet=True, arguments=arguments, stdout=stdout, stderr=stderr, state=BACKGROUND)
        runner.waitForSignal(stdout, expr='TEN gateway started', timeout=30)
        return hprocess, port

    def is_ten(self):
        """Return true if we are running against a Ten network. """
        return self.env in ['ten.sepolia', 'ten.uat', 'ten.dev', 'ten.local', 'ten.sim']

    def is_local_ten(self):
        """Return true if we are running against a local Ten network. """
        return self.env in ['ten.local']

    def is_sepolia_ten(self):
        """Return true if we are running against a sepolia Ten network. """
        return self.env in ['ten.sepolia']

    def is_uat_ten(self):
        """Return true if we are running against a sepolia Ten network. """
        return self.env in ['ten.uat']

    def fund_eth_from_faucet_server(self, runner):
        """Allocates native ETH to a users account from the faucet server. """
        account = Web3().eth.account.from_key(Properties().fundacntpk())
        url = '%s/fund/eth' % Properties().faucet_url(self.env)
        runner.log.info('Running request on %s', url)
        runner.log.info('Running for user address %s', account.address)
        headers = {'Content-Type': 'application/json'}
        data = {"address": account.address}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if not response.ok: runner.log.info('Request for funds was not successful, response text: %s', response.text)

    def __print_cost(self, runner, url, web3, user_id, eth_price):
        """Print out balances. """
        try:
            delta = 0
            for fn in Properties().accounts():
                account = web3.eth.account.from_key(fn())
                self.__register(account, url, user_id)

                balance = web3.from_wei(web3.eth.get_balance(account.address), 'ether')
                if fn.__name__ in self.balances:
                    delta = delta + (self.balances[fn.__name__] - balance)

            sign = '-' if delta < 0 else ''
            runner.log.info(' ')
            runner.log.info("  %s: %s%d WEI", 'Total cost', sign, Web3().to_wei(abs(delta), 'ether'),
                            extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
            runner.log.info("  %s: %s%.9f ETH", 'Total cost', sign, abs(delta), extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
            if eth_price is not None:
                runner.log.info("  %s: %s%.6f USD", 'Total cost', sign, abs(float(delta)*eth_price), extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
        except Exception as e:
            pass

    def get_eth_price(self):
        try:
            url = "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD"
            response = requests.get(url)
            if response.status_code == 200: return float(response.json()['USD'])
        except: return None
        return None

    @staticmethod
    def __stop_process(hprocess):
        """Stop a process started by this runner plugin. """
        hprocess.stop()

    def __join(self, url):
        """Join the ten network to get a token."""
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.get(url,  headers=headers)
        return response.text

    def __register(self, account, url, user_id):
        """Authenticate a user against the token. """
        domain = {'name': 'Ten', 'version': '1.0', 'chainId': Properties().chain_id(self.env), 'verifyingContract': '0x0000000000000000000000000000000000000000'}
        types = {
            'Authentication': [
                {'name': 'Encryption Token', 'type': 'address'},
            ],
        }
        message = {'Encryption Token': "0x"+user_id}

        signable_msg_from_dict = encode_typed_data(domain, types, message)
        signed_msg_from_dict = Account.sign_message(signable_msg_from_dict, account.key)

        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        data = {"signature": signed_msg_from_dict.signature.hex(), "address": account.address}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return response

    def __set_contract_addresses(self, runner):
        """Get the contract addresses and set into the properties. """
        data = {"jsonrpc": "2.0", "method": "ten_config", "id": self.MSG_ID}
        response = self.post(runner, data)
        if 'result' in response.json():
            config = response.json()['result']
            Properties.L1MessageBusAddress = Web3.to_checksum_address(config["L1MessageBus"])
            Properties.L2MessageBusAddress = Web3.to_checksum_address(config["L2MessageBus"])
            Properties.L1BridgeAddress = Web3.to_checksum_address(config["L1Bridge"])
            Properties.L2BridgeAddress = Web3.to_checksum_address(config["L2Bridge"])
            Properties.L1CrossChainManagementAddress = Web3.to_checksum_address(config["CrossChain"])
            Properties.L1CrossChainMessengerAddress = Web3.to_checksum_address(config["L1CrossChainMessenger"])
            Properties.L2CrossChainMessengerAddress = Web3.to_checksum_address(config["L2CrossChainMessenger"])
            if "PublicSystemContracts" in config:
                contracts = config["PublicSystemContracts"]
                Properties.L2PublicCallbacks = self.__get_contract(contracts, "PublicCallbacks")
        elif 'error' in response.json():
            runner.log.warn('Error getting contract address from ten_config')
            runner.log.error(response.json()['error']['message'])

    def __get_contract(self, contracts, key):
        return contracts[key] if key in contracts else None

    def post(self, runner, data):
        self.MSG_ID += 1
        server = 'http://%s:%s' % (Properties().node_host(self.env, self.NODE_HOST), Properties().node_port_http(self.env))
        return requests.post(server, json=data)
