import requests, json
from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):
    THRESHOLD = 5

    def execute(self):
        network = self.get_l1_network_connection(self.env)
        url = network.connection_url()
        web3 = Web3(Web3.HTTPProvider(url))

        sequencer_address = Properties().sequencer_address(key='obscuro.sepolia')
        sequencer_balance = web3.fromWei(web3.eth.get_balance(sequencer_address), 'ether')
        self.log.info('Sequencer account %s balance %.6f %s', sequencer_address, sequencer_balance, network.CURRENCY)

        validator_address = Properties().validator_address(key='obscuro.sepolia')
        validator_balance = web3.fromWei(web3.eth.get_balance(validator_address), 'ether')
        self.log.info('Validator account %s balance %.6f %s', validator_address, validator_balance, network.CURRENCY)

        deployer_address = Properties().l1_deployer_address(key='obscuro.sepolia')
        deployer_balance = web3.fromWei(web3.eth.get_balance(deployer_address), 'ether')
        self.log.info('Deployer account %s balance %.6f %s', deployer_address, deployer_balance, network.CURRENCY)

        faucet_balance = web3.fromWei(self.get_faucet_balance(), 'ether')
        self.log.info('Faucet balance %.6f %s', faucet_balance, network.CURRENCY)

        self.assertTrue(sequencer_balance >= self.THRESHOLD, assertMessage='L1 Sequence balance is below threshold')
        self.assertTrue(validator_balance >= self.THRESHOLD, assertMessage='L1 Validator balance is below threshold')
        self.assertTrue(deployer_balance >= self.THRESHOLD, assertMessage='L1 Deployer balance is below threshold')
        self.assertTrue(faucet_balance >= self.THRESHOLD, assertMessage='L2 Faucet balance is below threshold')

    def get_faucet_balance(self):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        url = '%s/balance' % Properties().faucet_url(self.env)
        response = requests.get(url, headers=headers)
        response_data = json.loads(response.text)
        return int(response_data.get('balance'))