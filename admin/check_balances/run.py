from web3 import Web3
from pysys.basetest import BaseTest
from obscuro.test.networks.sepolia import Sepolia
from obscuro.test.utils.properties import Properties


class PySysTest(BaseTest):
    THRESHOLD = 5

    def execute(self):
        network = Sepolia(self)
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

        self.assertTrue(sequencer_balance >= self.THRESHOLD, assertMessage='Sequence balance is below threshold')
        self.assertTrue(validator_balance >= self.THRESHOLD, assertMessage='Validator balance is below threshold')
        self.assertTrue(deployer_balance >= self.THRESHOLD, assertMessage='Deployer balance is below threshold')