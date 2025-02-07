import requests, json, time
from web3 import Web3
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):
    L1_THRESHOLD = 5
    L2_THRESHOLD = 25

    def execute(self):
        current_time = int(time.time())

        network = self.get_l1_network_connection(self.env)
        url = network.connection_url()
        web3 = Web3(Web3.HTTPProvider(url))

        sequencer_address = Properties().sequencer_address(key='ten.sepolia')
        sequencer_balance = web3.from_wei(web3.eth.get_balance(sequencer_address), 'ether')
        self.log.info('Sequencer account %s balance %.9f ETH', sequencer_address, sequencer_balance)

        validator1_address = Properties().validator1_address(key='ten.sepolia')
        validator1_balance = web3.from_wei(web3.eth.get_balance(validator1_address), 'ether')
        self.log.info('Validator 1 account %s balance %.9f ETH', validator1_address, validator1_balance)

        validator2_address = Properties().validator2_address(key='ten.sepolia')
        validator2_balance = web3.from_wei(web3.eth.get_balance(validator2_address), 'ether')
        self.log.info('Validator 2 account %s balance %.9f ETH', validator2_address, validator2_balance)

        deployer_address = Properties().l1_deployer_address(key='ten.sepolia')
        deployer_balance = web3.from_wei(web3.eth.get_balance(deployer_address), 'ether')
        self.log.info('Deployer account %s balance %.9f ETH', deployer_address, deployer_balance)

        faucet_address = Properties().l2_faucet_address(key='ten.sepolia')
        faucet_balance_wei = self.get_faucet_balance()
        faucet_balance_eth = web3.from_wei(faucet_balance_wei, 'ether')
        self.log.info('Faucet balance %.9f ETH', faucet_balance_eth)
        self.funds_db.insert_funds('Faucet', faucet_address, self.env, current_time, faucet_balance_wei)

        self.assertTrue(sequencer_balance >= self.L1_THRESHOLD,
                        assertMessage='L1 Sequencer balance is below threshold %s' % self.L1_THRESHOLD)
        self.assertTrue(validator1_balance >= self.L1_THRESHOLD,
                        assertMessage='L1 Validator1 balance is below threshold %s' % self.L1_THRESHOLD)
        self.assertTrue(validator2_balance >= self.L1_THRESHOLD,
                        assertMessage='L1 Validator2 balance is below threshold %s' % self.L1_THRESHOLD)
        self.assertTrue(deployer_balance >= self.L1_THRESHOLD, 
                        assertMessage='L1 Deployer balance is below threshold %s' % self.L1_THRESHOLD)
        self.assertTrue(faucet_balance_eth >= self.L2_THRESHOLD,
                        assertMessage='L2 Faucet balance is below threshold %s' % self.L2_THRESHOLD)

    def get_faucet_balance(self):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        url = '%s/balance' % Properties().faucet_url(self.env)
        response = requests.get(url, headers=headers)
        response_data = json.loads(response.text)
        return int(response_data.get('balance'))