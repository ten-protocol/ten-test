import re, json, os, shutil, copy
from web3 import Web3
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        project = os.path.join(self.output, 'project')
        private_key = self.get_ephemeral_pk()

        # connect to the network
        network_1 = self.get_network_connection()
        self.distribute_native(Web3().eth.account.from_key(private_key), network_1.ETH_ALLOC_EPHEMERAL)

        # copy over and initialise the project
        shutil.copytree(self.input, project)
        self.run_npm(args=['install', '--yes'], stdout='npm.out', stderr='npm.err', working_dir=project)

        # deploy and get the address from the hardhat output
        environ = copy.deepcopy(os.environ)
        environ['PK'] = private_key
        environ['CHAINID'] = str(network_1.chain_id())
        environ['HOST'] = network_1.HOST
        environ['PORT'] = str(network_1.PORT)
        self.run_npx(args=['hardhat', 'run', '--network', 'ten', 'scripts/deploy.js'],
                     working_dir=project, environ=environ, stdout='npx_deploy.out', stderr='npx_deploy.err')

        address = 'undefined'
        regex = re.compile('Contract deployed at (?P<address>.*)$', re.M)
        with open(os.path.join(self.output, 'npx_deploy.out'), 'r') as fp:
            for line in fp.readlines():
                result = regex.search(line)
                if result is not None: address = result.group('address')
        self.log.info('Contract deployed at address %s', address)

        abi_path = os.path.join(self.output, 'project', 'artifacts', 'contracts', 'Game.sol', 'Game.json')

        # connect account 1 and send some transactions
        web3_1, account_1 = network_1.connect_account1(self)
        block_number = web3_1.eth.get_block_number()
        with open(abi_path) as f: contract_1 = web3_1.eth.contract(address=address, abi=json.load(f)['abi'])
        for i in range(1,5): network_1.transact(self, web3_1, contract_1.functions.guess(i), account_1, 3_000_000)

        # connect account 2 and poll to get events
        network_2 = self.get_network_connection()
        network_2.connect_account2(self)
        self.get_logs(network_2, address, abi_path, block_number)

    def get_logs(self, network, address, abi_path, block_numer):
        # run a javascript by the dev to get past events
        self.log.info('Get past events for subscriber')
        stdout = os.path.join(self.output, 'poller.out')
        stderr = os.path.join(self.output, 'poller.err')
        logout = os.path.join(self.output, 'poller.log')
        script = os.path.join(self.input, 'poller.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--address', '%s' % address])
        args.extend(['--contract_abi', '%s' % abi_path])
        args.extend(['--log_file', '%s' % logout])
        args.extend(['--from_block', '%s' % block_numer])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Completed task', timeout=30)

        self.assertLineCount(file=logout, expr='Guessed event:', condition='==4')
        self.assertOrderedGrep(file=logout, exprList=['guessedNumber = %d' % d for d in range(1,5)])
        self.assertLineCount(file=logout, expr='Attempts event:', condition='==4')
        self.assertOrderedGrep(file=logout, exprList=['attempts = %d' % d for d in range(1,5)])
