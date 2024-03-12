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
        self.run_npm(args=['install', '--yes'], stdout='npm1.out', stderr='npm1.err', working_dir=project)

        # deploy and get the address from the hardhat output
        environ = copy.deepcopy(os.environ)
        environ['PK'] = private_key
        environ['HOST'] = network.HOST
        environ['PORT'] = str(network.PORT)
        self.run_npx(args=['hardhat', 'run', '--network', 'ten', 'scripts/deploy.js'],
                     working_dir=project, environ=environ, stdout='npx_deploy.out', stderr='npx_deploy.err')

        address = 'undefined'
        regex = re.compile('Incrementer proxy deployed to (?P<address>.*)$', re.M)
        with open(os.path.join(self.output, 'npx_deploy.out'), 'r') as fp:
            for line in fp.readlines():
                result = regex.search(line)
                if result is not None: address = result.group('address')
        self.log.info('Incrementer proxy deployed to address %s', address)

