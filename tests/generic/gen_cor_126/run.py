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


