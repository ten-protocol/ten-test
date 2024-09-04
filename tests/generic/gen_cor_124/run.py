import re, json, secrets
import os, shutil, copy
from web3 import Web3
from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):

    def get_network(self):
        return 'ten' if self.is_ten() else self.mode

    def execute(self):
        project = os.path.join(self.output, 'project')
        private_key_1 = secrets.token_hex(32)
        private_key_2 = secrets.token_hex(32)

        # connect to the network, allocate the normal ephemeral amount
        network = self.get_network_connection()
        self.distribute_native(Web3().eth.account.from_key(private_key_1), network.ETH_ALLOC)
        self.distribute_native(Web3().eth.account.from_key(private_key_2), network.ETH_ALLOC)
        web3, account = network.connect(self, private_key=private_key_1, check_funds=False)
        _, _ = network.connect(self, private_key=private_key_2, check_funds=False)

        # copy over and initialise the project
        shutil.copytree(self.input, project)
        self.run_npm(args=['install', '--yes'], stdout='npm.out', stderr='npm.err', working_dir=project)

        # deploy and get the address from the hardhat output
        environ = copy.deepcopy(os.environ)
        environ['PK1'] = private_key_1
        environ['PK2'] = private_key_2
        environ['HOST'] = network.HOST
        environ['PORT'] = str(network.PORT)
        environ['TOKEN'] = network.ID if self.is_ten() else ''
        self.run_npx(args=['hardhat', 'run', '--network', self.get_network(), 'scripts/deploy.js'],
                     working_dir=project, environ=environ, stdout='npx_deploy.out', stderr='npx_deploy.err')

        address = 'undefined'
        regex = re.compile('Proxy deployed at (?P<address>.*)$', re.M)
        with open(os.path.join(self.output, 'npx_deploy.out'), 'r') as fp:
            for line in fp.readlines():
                result = regex.search(line)
                if result is not None: address = result.group('address')
        self.log.info('Proxy deployed at address %s', address)

        # validate the proxy ownership is reported as changed
        expr_list = []
        expr_list.append('1 proxies ownership transferred through proxy admin')
        expr_list.append('%s.*transparent' % address)
        self.assertOrderedGrep('npx_deploy.out', exprList=expr_list)

        # check the initial value is set
        with open(os.path.join(self.output, 'project', 'artifacts', 'contracts', 'StoreV1.sol', 'StoreV1.json')) as f:
            contract = web3.eth.contract(address=address, abi=json.load(f)['abi'])
        ret = int(contract.functions.retrieve().call())
        self.log.info('Returned value is %d', ret)
        self.assertTrue(ret == 100)

        # upgrade the contract, set and retrieve the value
        environ['ADDRESS'] = address
        self.run_npx(args=['hardhat', 'run', '--network', self.get_network(), 'scripts/upgrade.js'],
                     working_dir=project, environ=environ, stdout='npx_upgrade.out', stderr='npx_upgrade.err')

        with open(os.path.join(self.output, 'project', 'artifacts', 'contracts', 'StoreV2.sol', 'StoreV2.json')) as f:
            contract = web3.eth.contract(address=address, abi=json.load(f)['abi'])
        network.transact(self, web3, contract.functions.store(400), account, 3_000_000, persist_nonce=False)
        ret = int(contract.functions.retrieve().call())
        self.log.info('Returned value is %d', ret)
        self.assertTrue(ret == 800)