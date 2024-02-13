import re, json, secrets
import os, shutil, copy
from web3 import Web3
from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):

    def get_network(self):
        return 'ten' if self.is_ten() else self.mode

    def execute(self):
        project = os.path.join(self.output, 'project')
        private_key = secrets.token_hex(32)

        # connect to the network
        network = self.get_network_connection()
        self.distribute_native(Web3().eth.account.from_key(private_key), network.ETH_ALLOC_EPHEMERAL)

        # copy over and initialise the project
        shutil.copytree(self.input, project)
        self.run_npm(args=['install', 'hardhat', '--yes'], stdout='npm1.out', stderr='npm1_err', working_dir=project)
        self.run_npm(args=['install', 'dotenv', '--yes'], stdout='npm2.out', stderr='npm2_err', working_dir=project)
        self.run_npm(args=['install', 'ten-hardhat-plugin', '--yes'], stdout='npm3.out', stderr='npm3_err', working_dir=project)

        # deploy and get the address from the hardhat output
        environ = copy.deepcopy(os.environ)
        environ['PK'] = private_key
        environ['HOST'] = network.HOST
        environ['PORT'] = str(network.PORT)
        self.run_npx(args=['hardhat', 'run', '--network', self.get_network(), 'scripts/deploy.js'],
                     working_dir=project, environ=environ, stdout='npx_deploy.out', stderr='npx_deploy.err')

        address = 'undefined'
        regex = re.compile('Contract deployed at (?P<address>.*)$', re.M)
        with open(os.path.join(self.output, 'npx_deploy.out'), 'r') as fp:
            for line in fp.readlines():
                result = regex.search(line)
                if result is not None: address = result.group('address')
        self.log.info('TestMaths contract deployed at address %s', address)

        # construct an instance of the contract from the address and abi
        with open(os.path.join(self.output, 'project', 'artifacts', 'contracts', 'Double.sol', 'Double.json')) as f:
            contract = web3.eth.contract(address=address, abi=json.load(f)['abi'])

        # make a call and assert we get the correct returned result
        ret = int(contract.functions.doIt(2).call())
        self.log.info('Returned value is %d', ret)
        self.assertTrue(ret == 4)
