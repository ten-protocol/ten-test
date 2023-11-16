import requests, json
from web3 import Web3
from ten.test.basetest import ObscuroNetworkTest
from ten.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):
    L1_THRESHOLD = 5
    L2_THRESHOLD = 10

    def execute(self):
        network = self.get_l1_network_connection(self.env)
        url = network.connection_url()
        web3 = Web3(Web3.HTTPProvider(url))

        sequencer_address = Properties().sequencer_address(key='ten.sepolia')
        sequencer_balance = web3.fromWei(web3.eth.get_balance(sequencer_address), 'ether')
        self.log.info('Sequencer account %s balance %.6f ETH', sequencer_address, sequencer_balance)

        validator_address = Properties().validator_address(key='ten.sepolia')
        validator_balance = web3.fromWei(web3.eth.get_balance(validator_address), 'ether')
        self.log.info('Validator account %s balance %.6f ETH', validator_address, validator_balance)

        deployer_address = Properties().l1_deployer_address(key='ten.sepolia')
        deployer_balance = web3.fromWei(web3.eth.get_balance(deployer_address), 'ether')
        self.log.info('Deployer account %s balance %.6f ETH', deployer_address, deployer_balance)

        faucet_balance = web3.fromWei(self.get_faucet_balance(), 'ether')
        self.log.info('Faucet balance %.6f ETH', faucet_balance)

        self.assertTrue(sequencer_balance >= self.L1_THRESHOLD,
                        assertMessage='L1 Sequence balance is below threshold %s' % self.L1_THRESHOLD)
        self.assertTrue(validator_balance >= self.L1_THRESHOLD,
                        assertMessage='L1 Validator balance is below threshold %s' % self.L1_THRESHOLD)
        self.assertTrue(deployer_balance >= self.L1_THRESHOLD, 
                        assertMessage='L1 Deployer balance is below threshold %s' % self.L1_THRESHOLD)
        self.assertTrue(faucet_balance >= self.L2_THRESHOLD,
                        assertMessage='L2 Faucet balance is below threshold %s' % self.L2_THRESHOLD)

    def get_faucet_balance(self):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        url = '%s/balance' % Properties().faucet_url(self.env)
        response = requests.get(url, headers=headers)
        response_data = json.loads(response.text)
        return int(response_data.get('balance'))