import os, shutil, copy
from ten.test.basetest import GenericNetworkTest
from ten.test.utils.properties import Properties


class PySysTest(GenericNetworkTest):

    def execute(self):
        project = os.path.join(self.output, 'project')

        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # copy over and initialise the project
        shutil.copytree(self.input, project)
        self.run_npm(args=['install', 'hardhat', '--yes'],
                     stdout='npm_init_hh.out', stderr='npm_init_hh_err', working_dir=project)
        self.run_npm(args=['install', 'dotenv', '--yes'],
                     stdout='npm_init_de.out', stderr='npm_init_de_err', working_dir=project)

        environ = copy.deepcopy(os.environ)
        environ['PK'] = Properties().account1pk()
        environ['HOST'] = network.HOST
        environ['PORT'] = str(network.PORT)
        environ['TOKEN'] = network.ID if self.is_ten() else ''
        self.run_npx(args=['hardhat', 'run', '--network', 'ten', 'scripts/deploy.js'],
                     working_dir=project, environ=environ, stdout='npx_deploy.out', stderr='npx_deploy.err')

