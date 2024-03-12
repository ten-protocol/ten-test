import secrets
import os, shutil, copy
from web3 import Web3
from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):

    def execute(self):
        project = os.path.join(self.output, 'project')
        private_key_1 = secrets.token_hex(32)
        private_key_2 = secrets.token_hex(32)

        # connect to the network
        network = self.get_network_connection()
        account_1 = Web3().eth.account.from_key(private_key_1)
        account_2 = Web3().eth.account.from_key(private_key_2)
        self.distribute_native(account_1, network.ETH_ALLOC_EPHEMERAL)
        self.distribute_native(account_2, network.ETH_ALLOC_EPHEMERAL)

        # copy over and initialise the project
        shutil.copytree(self.input, project)
        self.run_npm(args=['install', '--yes'], stdout='npm.out', stderr='npm.err', working_dir=project)

        # deploy and get the address from the hardhat output
        environ = copy.deepcopy(os.environ)
        environ['PK1'] = private_key_1
        environ['PK2'] = private_key_2
        environ['HOST'] = network.HOST
        environ['PORT'] = str(network.PORT)
        self.run_npx(args=['hardhat', 'deploy', '--network', 'ten'],
                     working_dir=project, environ=environ, stdout='npx_deploy.out', stderr='npx_deploy.err')

        self.assertGrep('npx_deploy.out', expr='Found 2 signers configured for this network')
        self.assertGrep('npx_deploy.out', expr='Registering account %s...' % account_1.address)
        self.assertGrep('npx_deploy.out', expr='Registering account %s...' % account_2.address)
        self.assertGrep('npx_deploy.out', expr='deploying "Double" .*deployed at .* with .* gas')
        self.assertGrep('npx_deploy.out', expr='deploying "Triple" .*deployed at .* with .* gas')
