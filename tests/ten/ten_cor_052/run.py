import re, json, secrets
import os, shutil, copy
from web3 import Web3
from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):

    def execute(self):
        project = os.path.join(self.output, 'project')
        private_key = secrets.token_hex(32)

        # connect to the network
        network = self.get_network_connection()
        self.distribute_native(Web3().eth.account.from_key(private_key), network.ETH_ALLOC_EPHEMERAL)

        # copy over and initialise the project
        shutil.copytree(self.input, project)
        self.run_npm(args=['install', '--yes'], stdout='npm.out', stderr='npm.err', working_dir=project)

        # deploy and get the address from the hardhat output
        environ = copy.deepcopy(os.environ)
        environ['PK'] = private_key
        environ['HOST'] = network.HOST
        environ['PORT'] = str(network.PORT)
        self.run_npx(args=['hardhat', 'run', '--network', 'ten', 'scripts/deploy.js'],
                     working_dir=project, environ=environ, stdout='npx_deploy.out', stderr='npx_deploy.err')

        address = 'undefined'
        regex = re.compile('Incrementer proxy deployed to: (?P<address>.*)$', re.M)
        with open(os.path.join(self.output, 'npx_deploy.out'), 'r') as fp:
            for line in fp.readlines():
                result = regex.search(line)
                if result is not None: address = result.group('address')
        self.log.info('Incrementer proxy deployed to address %s', address)

        # construct an instance of the contract from the address and abi
        web3, account = network.connect_account1(self)
        with open(os.path.join(self.output, 'project', 'artifacts', 'contracts', 'IncrementerV1.sol', 'IncrementerV1.json')) as f:
            contract = web3.eth.contract(address=address, abi=json.load(f)['abi'])

        # make a call and assert we get the correct returned result
        network.transact(self, web3, contract.functions.initialValue(2), account, 3_000_000)
        network.transact(self, web3, contract.functions.increase(), account, 3_000_000)
        ret = int(contract.functions.retrieve().call())
        self.log.info('Returned value is %d', ret)
        self.assertTrue(ret == 3)
