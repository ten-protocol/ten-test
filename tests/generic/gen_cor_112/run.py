import secrets, os
from web3 import Web3
from ten.test.contracts.storage import KeyStorage
from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):
    ITERATIONS = 10
    CLIENTS = 5

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        contract = KeyStorage(self, web3)
        contract.deploy(network, account)

        # estimate how much gas is needed and then make the transaction via ethers
        chain_id = network.chain_id()
        gas_price = web3.eth.gas_price
        params = {'from': account.address, 'chainId': chain_id, 'gasPrice': gas_price}
        gas_limit = contract.contract.functions.setItem("1", 1).estimate_gas(params)
        funds_needed = 1.1 * (gas_price * gas_limit)

        self.client(network, contract, 'meaning_of_life', 42, web3.from_wei(funds_needed, 'ether'))
        value_after = contract.contract.functions.getItem('meaning_of_life').call()
        self.log.info('The meaning of life is ... %d', value_after)
        self.assertTrue(value_after == 42)

    def client(self, network, contract, key, value, funds_needed):
        private_key = secrets.token_hex(32)
        self.distribute_native(Web3().eth.account.from_key(private_key), funds_needed, 'ether')
        network.connect(self, private_key=private_key, check_funds=False)

        # create the client
        stdout = os.path.join(self.output, 'client.out')
        stderr = os.path.join(self.output, 'client.err')
        logout = os.path.join(self.output, 'client.log')
        script = os.path.join(self.input, 'client.js')
        args = []
        args.extend(['--network', network.connection_url()])
        args.extend(['--address', contract.address])
        args.extend(['--contract_abi', contract.abi_path])
        args.extend(['--private_key', private_key])
        args.extend(['--key', key])
        args.extend(['--value', str(value)])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Starting transactions', timeout=10)
        self.waitForGrep(file=logout, expr='Completed transactions', timeout=40)
