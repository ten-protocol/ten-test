import re, json
import os, shutil, copy
from web3 import Web3
from ten.test.basetest import GenericNetworkTest
from ten.test.utils.properties import Properties


class PySysTest(GenericNetworkTest):

    def get_network(self):
        return 'ten' if self.is_ten() else self.mode

    def execute(self):
        project = os.path.join(self.output, 'project')
        private_key_1 = self.get_ephemeral_pk()
        private_key_2 = self.get_ephemeral_pk()

        # connect to the network, allocate the normal ephemeral amount
        network = self.get_network_connection()
        self.distribute_native(Web3().eth.account.from_key(private_key_1), network.ETH_ALLOC)
        web3_1, account_1 = network.connect(self, private_key=private_key_1, check_funds=False)

        self.distribute_native(Web3().eth.account.from_key(private_key_2), network.ETH_ALLOC)
        web3_2, account_2 = network.connect(self, private_key=private_key_2, check_funds=False)

        # copy over and initialise the project
        shutil.copytree(self.input, project)
        self.run_npm(args=['install', '--yes'], stdout='npm.out', stderr='npm.err', working_dir=project)

        # deploy and get the address from the hardhat output
        environ = copy.deepcopy(os.environ)
        environ['PK'] = private_key_1
        environ['CHAINID'] = network.chain_id()
        environ['HOST'] = network.HOST
        environ['PORT'] = str(network.PORT)
        environ['TOKEN'] = self.get_token(network)
        self.run_npx(args=['hardhat', 'run', '--network', self.get_network(), 'scripts/deploy.js'],
                     working_dir=project, environ=environ, stdout='npx_deploy.out', stderr='npx_deploy.err')

        address = 'undefined'
        regex = re.compile('Proxy deployed at (?P<address>.*)$', re.M)
        with open(os.path.join(self.output, 'npx_deploy.out'), 'r') as fp:
            for line in fp.readlines():
                result = regex.search(line)
                if result is not None: address = result.group('address')
        self.log.info('Proxy deployed at address %s', address)
        self.wait(float(self.block_time))

        # construct an instance of the contract from the address and abi
        with open(os.path.join(self.output, 'project', 'artifacts', 'contracts', 'StoreV1.sol', 'StoreV1.json')) as f:
            contract = web3_2.eth.contract(address=address, abi=json.load(f)['abi'])

        # store a value in the contract and retrieve it
        network.transact(self, web3_2, contract.functions.store(200), account_2, 3_000_000, persist_nonce=False)
        ret = int(contract.functions.retrieve().call())
        self.log.info('Returned value is %d', ret)
        self.assertTrue(ret == 200)

        # upgrade the contract
        environ['ADDRESS'] = address
        self.run_npx(args=['hardhat', 'run', '--network', self.get_network(), 'scripts/upgrade.js'],
                     working_dir=project, environ=environ, stdout='npx_upgrade.out', stderr='npx_upgrade.err')
        self.waitForSignal(file=os.path.join(self.output, 'npx_upgrade.out'), expr='StoreV2 deployed to')
        self.wait(float(self.block_time))

        # make a call to v2 and assert we get the correct returned result, then repeat
        with open(os.path.join(self.output, 'project', 'artifacts', 'contracts', 'StoreV2.sol', 'StoreV2.json')) as f:
            contract = web3_2.eth.contract(address=address, abi=json.load(f)['abi'])
        count = 0
        while(True):
            ret = int(contract.functions.retrieve().call())
            self.log.info('Looping ... returned value is %d', ret)
            if ret == 400: break
            self.wait(1.0)
            count += 1
            if count>10: break
        self.assertTrue(ret == 400)

        # store a value in the contract and retrieve it again
        network.transact(self, web3_2, contract.functions.store(400), account_2, 3_000_000, persist_nonce=False)
        ret = int(contract.functions.retrieve().call())
        self.log.info('Returned value is %d', ret)
        self.assertTrue(ret == 800)

    def get_token(self, network):
        if self.is_ten(): return network.ID
        if self.mode == 'sepolia': return Properties().sepoliaAPIKey()
        return ''
