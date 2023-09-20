import os, shutil, sys, json, requests
from collections import OrderedDict
from web3 import Web3
from pathlib import Path
from eth_account.messages import encode_defunct
from pysys.constants import PROJECT, BACKGROUND
from pysys.exceptions import AbortExecution
from pysys.constants import LOG_TRACEBACK
from pysys.utils.logutils import BaseLogFormatter
from obscuro.test.persistence.nonce import NoncePersistence
from obscuro.test.persistence.contract import ContractPersistence
from obscuro.test.utils.properties import Properties


class ObscuroRunnerPlugin():
    """Runner class for running a set of tests against a given environment.

    The runner is responsible for starting any applications prior to running the requested tests. When running
    against Ganache, a local Ganache will be started. All processes started by the runner are automatically stopped
    when the tests are complete. Note the runner should remain independent to the BaseTest, i.e. is stand alone as
    much as possible. This is because most of the framework is written to be test centric.
    """

    def __init__(self):
        """Constructor. """
        self.env = None
        self.NODE_HOST = None
        self.balances = OrderedDict()

    def setup(self, runner):
        """Set up a runner plugin to start any processes required to execute the tests. """
        self.env = 'obscuro' if runner.mode is None else runner.mode
        self.NODE_HOST = runner.getXArg('NODE_HOST', '')
        if self.NODE_HOST == '': self.NODE_HOST = None
        runner.output = os.path.join(PROJECT.root, '.runner')
        runner.log.info('Runner is executing against environment %s', self.env)

        # create dir for any runner output
        if os.path.exists(runner.output): shutil.rmtree(runner.output)
        os.makedirs(runner.output)

        # create the nonce db if it does not already exist, clean it out if using ganache
        db_dir = os.path.join(str(Path.home()), '.obscurotest')
        if not os.path.exists(db_dir): os.makedirs(db_dir)
        nonce_db = NoncePersistence(db_dir)
        nonce_db.create()
        contracts_db = ContractPersistence(db_dir)
        contracts_db.create()

        if self.is_obscuro() and runner.threads > 3:
            raise Exception('Max threads against Obscuro cannot be greater than 3')
        elif self.env == 'ganache' and runner.threads > 3:
            raise Exception('Max threads against Ganache cannot be greater than 3')
        elif self.env == 'goerli' and runner.threads > 1:
            raise Exception('Max threads against Goerli cannot be greater than 1')

        try:
            if self.is_obscuro():
                props = Properties()
                gateway_url = None
                account = Web3().eth.account.privateKeyToAccount(Properties().fundacntpk())

                if self.is_local_obscuro():
                    hprocess, port = self.run_wallet(runner)
                    gateway_url = 'http://127.0.0.1:%d' % port
                    runner.log.info('Joining network using url %s', '%s/v1/join/' % gateway_url)
                    user_id = self.__join('%s/v1/join/' % gateway_url)

                    runner.log.info('Registering account %s with the network', account.address)
                    response = self.__register(account, '%s/v1/authenticate/?u=%s' % (gateway_url, user_id), user_id)
                    runner.log.info('Registration success was %s', response.ok)
                    web3 = Web3(Web3.HTTPProvider('%s/v1/?u=%s' % (gateway_url, user_id)))
                    runner.addCleanupFunction(lambda: self.__print_cost(runner,
                                                                        '%s/v1/authenticate/?u=%s' % (gateway_url, user_id),
                                                                        web3, user_id))
                    runner.addCleanupFunction(lambda: self.__stop_process(hprocess))
                else:
                    gateway_url = '%s' % (props.gateway_url(self.env))
                    runner.log.info('Joining network using url %s', '%s/v1/join/' % gateway_url)
                    user_id = self.__join('%s/v1/join/' % gateway_url)
                    runner.log.info('User id is %s', user_id)

                    runner.log.info('Registering account %s with the network', account.address)
                    response = self.__register(account, '%s/v1/authenticate/?u=%s' % (gateway_url, user_id), user_id)
                    runner.log.info('Registration success was %s', response.ok)
                    web3 = Web3(Web3.HTTPProvider('%s/v1/?u=%s' % (gateway_url, user_id)))
                    runner.addCleanupFunction(lambda: self.__print_cost(runner,
                                                                        '%s/v1/authenticate/?u=%s' % (gateway_url, user_id),
                                                                        web3, user_id))

                tx_count = web3.eth.get_transaction_count(account.address)
                balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')

                if tx_count == 0:
                    runner.log.info('Funded key tx count is zero ... clearing persistence')
                    nonce_db.delete_environment(self.env)
                    contracts_db.delete_environment(self.env)

                if balance < 200:
                    runner.log.info('Funded key balance below threshold ... making faucet call')
                    self.fund_obx_from_faucet_server(runner)
                    self.fund_obx_from_faucet_server(runner)

                runner.log.info('')
                runner.log.info('Accounts with non-zero funds;')
                for fn in Properties().accounts():
                    account = web3.eth.account.privateKeyToAccount(fn())
                    self.__register(account, '%s/v1/authenticate/?u=%s' % (gateway_url, user_id), user_id)

                    self.balances[fn.__name__] = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
                    if self.balances[fn.__name__] > 0:
                        runner.log.info("  Funds for %s: %.18f OBX", fn.__name__, self.balances[fn.__name__],
                                        extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
                runner.log.info('')

            elif self.env == 'ganache':
                nonce_db.delete_environment('ganache')
                hprocess = self.run_ganache(runner)
                runner.addCleanupFunction(lambda: self.__stop_process(hprocess))

        except AbortExecution as e:
            runner.log.info('Error executing runner plugin startup actions %s', e)
            runner.log.info('See contents of the .runner directory in the project root for any process output')
            runner.log.info('Exiting ...')
            runner.cleanup()
            sys.exit(1)

        nonce_db.close()
        contracts_db.close()

    def run_ganache(self, runner):
        """Run ganache for use by the tests. """
        runner.log.info('Starting ganache server to run tests through managed instance')
        stdout = os.path.join(runner.output, 'ganache.out')
        stderr = os.path.join(runner.output, 'ganache.err')
        port = Properties().port_http(key='ganache')

        arguments = []
        arguments.extend(('--port', str(port)))
        arguments.extend(('--account', '0x%s,5000000000000000000' % Properties().fundacntpk()))
        arguments.extend(('--gasLimit', '7200000'))
        arguments.extend(('--gasPrice', '1000'))
        arguments.extend(('--blockTime', Properties().block_time_secs(self.env)))
        arguments.extend(('-k', 'berlin'))
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
        runner.waitForSignal(stdout, expr='Wallet extension started', timeout=30)
        return hprocess, port

    def is_obscuro(self):
        """Return true if we are running against an Obscuro network. """
        return self.env in ['obscuro', 'obscuro.dev', 'obscuro.local']

    def is_local_obscuro(self):
        """Return true if we are running against a local Obscuro network. """
        return self.env in ['obscuro.local']

    def fund_obx_from_faucet_server(self, runner):
        """Allocates native OBX to a users account from the faucet server. """
        account = Web3().eth.account.privateKeyToAccount(Properties().fundacntpk())
        runner.log.info('Running request on %s', Properties().faucet_url(self.env))
        runner.log.info('Running for user address %s', account.address)
        headers = {'Content-Type': 'application/json'}
        data = {"address": account.address}
        requests.post(Properties().faucet_url(self.env), data=json.dumps(data), headers=headers)

    def __print_cost(self, runner, url, web3, user_id):
        """Print out balances. """
        try:
            delta = 0
            for fn in Properties().accounts():
                account = web3.eth.account.privateKeyToAccount(fn())
                self.__register(account, url, user_id)

                balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
                if fn.__name__ in self.balances:
                    delta = delta + (self.balances[fn.__name__] - balance)
            runner.log.info(' ')
            runner.log.info("%s: %d Wei", 'Total cost', Web3().toWei(delta, 'ether'),
                            extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
            runner.log.info("%s: %.9f ETH", 'Total cost', delta, extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
        except Exception as e:
            pass

    @staticmethod
    def __stop_process(hprocess):
        """Stop a process started by this runner plugin. """
        hprocess.stop()

    @staticmethod
    def __join(url):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.get(url,  headers=headers)
        return response.text

    @staticmethod
    def __register(account, url, user_id):
        text_to_sign = "Register " + user_id + " for " + str(account.address).lower()
        eth_message = f"{text_to_sign}"
        encoded_message = encode_defunct(text=eth_message)
        signature = account.sign_message(encoded_message)

        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        data = {"signature": signature['signature'].hex(), "message": text_to_sign}
        print(data)
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return response
