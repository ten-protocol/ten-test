import re, json
import os, shutil, copy
from web3 import Web3
from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):

    def execute(self):
        project = os.path.join(self.output, 'project')
        private_key = self.get_ephemeral_pk()

        # connect to the network, allocate the normal ephemeral amount for deployment
        network = self.get_network_connection()
        self.distribute_native(Web3().eth.account.from_key(private_key), network.ETH_ALLOC)
        web3, account = network.connect(self, private_key=private_key, check_funds=False)

        # connect the players of the game
        web3_1, account_1 = network.connect_account1(self)
        network_2 = self.get_network_connection()
        network_2.connect_account2(self)

        # copy over and initialise the project
        shutil.copytree(self.input, project)
        self.run_npm(args=['install', '--yes'], stdout='npm.out', stderr='npm.err', working_dir=project)

        # deploy and get the address from the hardhat output
        self.log.info('')
        self.log.info('Deploying GameV1 via a proxy')
        environ = copy.deepcopy(os.environ)
        environ['PK'] = private_key
        environ['CHAINID'] = str(network.chain_id())
        environ['HOST'] = network.HOST
        environ['PORT'] = str(network.PORT)
        environ['TOKEN'] = network.ID if self.is_ten() else ''
        self.run_npx(args=['hardhat', 'run', '--network', 'ten', 'scripts/deploy.js'],
                     working_dir=project, environ=environ, stdout='npx_deploy.out', stderr='npx_deploy.err')

        address = 'undefined'
        regex = re.compile('Proxy deployed at (?P<address>.*)$', re.M)
        with open(os.path.join(self.output, 'npx_deploy.out'), 'r') as fp:
            for line in fp.readlines():
                result = regex.search(line)
                if result is not None: address = result.group('address')
        self.log.info('Proxy deployed at address %s', address)
        self.wait(4*float(self.block_time))

        # construct an instance of the game_v1 contract from the address and abi
        abi_path = os.path.join(self.output,'project','artifacts','contracts','GameV1.sol', 'GameV1.json')
        with open(abi_path) as f: contract = web3.eth.contract(address=address, abi=json.load(f)['abi'])

        # grab the block number transact and see if account 2 can get any logs
        self.log.info('')
        block_number = web3_1.eth.get_block_number()
        network.transact(self, web3_1, contract.functions.guess(9), account_1, 3_000_000)
        logout = self.get_logs(network_2, address, abi_path, block_number, client='one')
        self.assertGrep(file=logout, expr='Guessed event:', contains=False)  # not relevant to this user
        self.assertGrep(file=logout, expr='Attempts event:', contains=False)

        # upgrade the contract (which now adds in a visibility config)
        self.log.info('')
        self.log.info('Upgrading to GameV2 via a proxy')
        environ['ADDRESS'] = address
        self.run_npx(args=['hardhat', 'run', '--network', 'ten', 'scripts/upgrade.js'],
                     working_dir=project, environ=environ, stdout='npx_upgrade.out', stderr='npx_upgrade.err')
        self.waitForSignal(file=os.path.join(self.output, 'npx_upgrade.out'), expr='GameV2 deployed to')
        self.wait(float(self.block_time))

        # construct an instance of the game_v2 contract from the address and abi
        abi_path = os.path.join(self.output,'project','artifacts','contracts','GameV1.sol', 'GameV1.json')
        with open(abi_path) as f: contract = web3.eth.contract(address=address, abi=json.load(f)['abi'])

        # grab the block number transact and see if account 2 can get any logs
        block_number = web3_1.eth.get_block_number()
        network.transact(self, web3_1, contract.functions.guess(15), account_1, 3_000_000)
        logout = self.get_logs(network_2, address, abi_path, block_number, client='two')
        self.assertGrep(file=logout, expr='Guessed event:', contains=False)  # not relevant to this user
        self.assertGrep(file=logout, expr='Attempts event:', contains=False)

    def get_logs(self, network, address, abi_path, block_numer, client):
        # run a javascript by the dev to get past events
        self.log.info('Get past events for subscriber')
        stdout = os.path.join(self.output, 'poller_%s.out' % client)
        stderr = os.path.join(self.output, 'poller_%s.err' % client)
        logout = os.path.join(self.output, 'poller_%s.log' % client)
        script = os.path.join(self.input, 'poller.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--address', '%s' % address])
        args.extend(['--contract_abi', '%s' % abi_path])
        args.extend(['--log_file', '%s' % logout])
        args.extend(['--from_block', '%s' % block_numer])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Completed task', timeout=30)
        return logout
