import os
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import Topic1CanViewGuessGame


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect the dev to the network to deploy the game
        network_dev = self.get_network_connection()
        web3_dev, account_dev = network_dev.connect_account2(self)
        block_number = web3_dev.eth.get_block_number()
        game = Topic1CanViewGuessGame(self, web3_dev)
        game.deploy(network_dev, account_dev)

        # connect a user to the network to play the game and make some guesses
        network_usr = self.get_network_connection()
        web3_usr, account_usr = network_usr.connect_account1(self)
        game_usr = Topic1CanViewGuessGame.clone(web3_usr, account_usr, game)
        target = game_usr.contract.functions.guess
        for i in range(1, 5): network_dev.transact(self, web3_usr, target(i), account_usr, game_usr.GAS_LIMIT)

        # run a javascript by the dev to get past events
        stdout = os.path.join(self.output, 'poller.out')
        stderr = os.path.join(self.output, 'poller.err')
        logout = os.path.join(self.output, 'poller.log')
        script = os.path.join(self.input, 'poller.js')
        args = []
        args.extend(['--network_ws', network_dev.connection_url(web_socket=True)])
        args.extend(['--address', '%s' % game.address])
        args.extend(['--contract_abi', '%s' % game.abi_path])
        args.extend(['--contract_abi', '%s' % game.abi_path])
        args.extend(['--log_file', '%s' % logout])
        args.extend(['--from_block', '%s' % block_number])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Completed task', timeout=30)

        self.assertLineCount(file=logout, expr='Guessed event', condition='==4')
        self.assertOrderedGrep(file=logout, exprList=['guessedNumber = %d' % d for d in range(1, 5)])
