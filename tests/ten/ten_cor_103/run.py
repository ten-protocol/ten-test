from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import Game
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway, and deploy the game contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        game = Game(self, web3)
        game.deploy(network, account)

        # run the event log subscriber and transact as account 1 (signed transactions)
        subscriber = AllEventsLogSubscriber(self, network, game.address, game.abi_path)
        subscriber.run()
        for i in range(1, 6):
            self.log.info('  Guessing number as account1: %d'%i)
            network.transact(self, web3, game.contract.functions.guess(i), account, game.GAS_LIMIT)

        # get a session key for this userid and fund it, activate the key
        sk = self.get_session_key(network.connection_url())
        tx = {'to': sk, 'value': web3.to_wei(0.01, 'ether'), 'gasPrice': web3.eth.gas_price}
        tx['gas'] = web3.eth.estimate_gas(tx)
        network.tx(self, web3, tx, account)
        self.activate_session_key(network.connection_url())

        # transact as the session key (unsigned transactions)
        for i in range(6, 11):
            self.log.info('  Guessing number as session key: %d'%i)
            network.transact_unsigned(self, web3, game.contract.functions.guess(i), sk, game.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # return the funds and deactivate
        tx = {'to': account.address, 'gasPrice': web3.eth.gas_price}
        tx['gas'] = web3.eth.estimate_gas(tx)
        tx['value'] = web3.eth.get_balance(sk) - (tx['gas'] * web3.eth.gas_price)
        network.tx_unsigned(self, web3, tx, sk)
        self.deactivate_session_key(network.connection_url())

        # assert that we see the event logs
        self.assertLineCount('subscriber.out', expr='Received event: Guessed', condition='==10')
        self.assertOrderedGrep('subscriber.out', exprList=['guessedNumber: \'%d\'' % x for x in range(1, 11)])
