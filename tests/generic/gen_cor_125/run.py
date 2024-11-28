import re, json, os, shutil, copy
from web3 import Web3
from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):

    def get_network(self):
        return 'ten' if self.is_ten() else self.mode

    def execute(self):
        project = os.path.join(self.output, 'project')
        private_key = self.get_ephemeral_pk()

        # connect to the network, allocate the normal ephemeral amount
        network = self.get_network_connection()
        self.distribute_native(Web3().eth.account.from_key(private_key), network.ETH_ALLOC)
        web3, account = network.connect(self, private_key=private_key, check_funds=False)

        # copy over and initialise the project
        shutil.copytree(self.input, project)
        self.run_npm(args=['install', '--yes'], stdout='npm.out', stderr='npm.err', working_dir=project)

        # deploy and get the address from the hardhat output
        environ = copy.deepcopy(os.environ)
        environ['PK'] = private_key
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
        self.wait(4*float(self.block_time))

        # construct an instance of the contract from the address and abi
        with open(os.path.join(self.output,'project','artifacts','contracts','MessageBusV2.sol', 'MessageBusV2.json')) as f:
            contract = web3.eth.contract(address=address, abi=json.load(f)['abi'])

        # make a call to v1 and assert we get the correct returned result
        ret = int(contract.functions.getVersion().call())
        self.log.info('Returned value is %d', ret)
        self.assertTrue(ret == 2)
