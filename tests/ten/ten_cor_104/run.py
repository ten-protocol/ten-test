from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import Game
from web3._utils.events import EventLogErrorFlags


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway, and deploy the game contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        game = Game(self, web3)
        game.deploy(network, account)

        # get a session key for this userid and fund it, activate the key
        sk = self.get_session_key(network.connection_url())
        tx = {'to': sk, 'value': web3.to_wei(0.01, 'ether'), 'gasPrice': web3.eth.gas_price}
        tx['gas'] = web3.eth.estimate_gas(tx)
        network.tx(self, web3, tx, account)
        self.activate_session_key(network.connection_url())

        # transact as the session key (unsigned transactions)
        receipt = network.transact_unsigned(self, web3, game.contract.functions.guess(2), sk, game.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        logs = game.contract.events.Guessed().process_receipt(receipt, EventLogErrorFlags.Discard)
        self.assertTrue(logs[0]['args']['guessedNumber'] == 2, assertMessage='Logs should show the guessed number as 2')
        logs = game.contract.events.Attempts().process_receipt(receipt, EventLogErrorFlags.Discard)
        self.assertTrue(logs[0]['args']['attempts'] == 1, assertMessage='Logs should show the number attempts as 1')

        # return the funds and deactivate
        tx = {'to': account.address, 'gasPrice': web3.eth.gas_price}
        tx['gas'] = web3.eth.estimate_gas(tx)
        tx['value'] = web3.eth.get_balance(sk) - (tx['gas'] * web3.eth.gas_price)
        network.tx_unsigned(self, web3, tx, sk)
        self.deactivate_session_key(network.connection_url())

