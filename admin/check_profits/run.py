import time
from web3 import Web3
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        current_time = int(time.time())

        l1_network = self.get_l1_network_connection(self.env)
        web3_sequencer = Web3(Web3.HTTPProvider(l1_network.connection_url()))
        sequencer_address = Properties().sequencer_address(key='ten.sepolia')
        sequencer_balance = web3_sequencer.eth.get_balance(sequencer_address)
        self.log.info('Sequencer balance %.6f ETH', web3_sequencer.from_wei(sequencer_balance, 'ether'))
        self.funds_db.insert_funds('Sequencer', sequencer_address, self.env, current_time, sequencer_balance)

        l2_network = self.get_network_connection()
        web3_payment, account_payment = l2_network.connect(self, Properties().l2_gas_payment_account_pk(self.env), check_funds=False)
        gas_payment_address = account_payment.address
        gas_payment_balance = web3_payment.eth.get_balance(gas_payment_address)
        self.log.info('Gas holding balance %.6f ETH', web3_sequencer.from_wei(gas_payment_balance, 'ether'))
        self.funds_db.insert_funds('GasPayment', gas_payment_address, self.env, current_time, gas_payment_balance)