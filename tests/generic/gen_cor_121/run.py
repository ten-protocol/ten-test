import re, json
import os, shutil, copy
from ten.test.basetest import GenericNetworkTest
from ten.test.utils.properties import Properties


class PySysTest(GenericNetworkTest):

    def get_network(self):
        return 'ten' if self.is_ten() else self.mode

    def execute(self):
        project = os.path.join(self.output, 'project')

        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # copy over and initialise the project
        shutil.copytree(self.input, project)
        self.run_npm(args=['install', 'hardhat', '--yes'], stdout='npm1.out', stderr='npm1_err', working_dir=project)
        self.run_npm(args=['install', 'dotenv', '--yes'], stdout='npm2.out', stderr='npm2_err', working_dir=project)

        # deploy and get the address from the hardhat output
        environ = copy.deepcopy(os.environ)
        environ['PK'] = Properties().account1pk()
        environ['HOST'] = network.HOST
        environ['PORT'] = str(network.PORT)
        environ['TOKEN'] = network.ID if self.is_ten() else ''
        environ['API_KEY'] = Properties().sepoliaAPIKey() if self.mode == 'sepolia' else ''
        self.run_npx(args=['hardhat', 'run', '--network', self.get_network(), 'scripts/deploy.js'],
                     working_dir=project, environ=environ, stdout='npx_deploy.out', stderr='npx_deploy.err')

        address = 'undefined'
        regex = re.compile('TestMaths deployed at (?P<address>.*)$', re.M)
        with open(os.path.join(self.output, 'npx_deploy.out'), 'r') as fp:
            for line in fp.readlines():
                result = regex.search(line)
                if result is not None: address = result.group('address')
        self.log.info('TestMaths contract deployed at address %s', address)

        # construct an instance of the contract from the address and abi
        with open(os.path.join(self.output,'project','artifacts','contracts','TestMath.sol','TestMath.json')) as f:
            contract = web3.eth.contract(address=address, abi=json.load(f)['abi'])

        # make a call and assert we get the correct returned result
        ret = int(contract.functions.testSquareRoot(25).call())
        self.log.info('Returned value is %d', ret)
        self.assertTrue(ret == 5)