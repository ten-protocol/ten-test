import os
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import FieldEveryoneGuessGame


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect the dev to the network to deploy the game
        network_dev = self.get_network_connection()
        web3_dev, account_dev = network_dev.connect_account2(self)
        block_number = web3_dev.eth.get_block_number()
        game = FieldEveryoneGuessGame(self, web3_dev)
        game.deploy(network_dev, account_dev)

        # connect a user to the network to play the game and make some guesses
        network_usr = self.get_network_connection()
        web3_usr, account_usr = network_usr.connect_account1(self)
        game_usr = FieldEveryoneGuessGame.clone(web3_usr, account_usr, game)
        target = game_usr.contract.functions.guess
        for i in range(1,5): network_dev.transact(self, web3_usr, target(i), account_usr, game_usr.GAS_LIMIT)

        # dev account can see the Guessed event but not the Attempts event
        logout = self.get_logs(network_dev, game, block_number, 'dev')
        self.assertLineCount(file=logout, expr='Guessed event:', condition='==4')
        self.assertOrderedGrep(file=logout, exprList=['guessedNumber = %d' % d for d in range(1,5)])
        self.assertLineCount(file=logout, expr='Attempts event:', condition='==0')

        # usr account can see the Guessed event and the Attempts event
        logout = self.get_logs(network_usr, game_usr, block_number, 'usr')
        self.assertLineCount(file=logout, expr='Guessed event:', condition='==4')
        self.assertOrderedGrep(file=logout, exprList=['guessedNumber = %d' % d for d in range(1,5)])
        self.assertLineCount(file=logout, expr='Attempts event:', condition='==4')
        self.assertOrderedGrep(file=logout, exprList=['attempts = %d' % d for d in range(1,5)])


    def get_logs(self, network, contract, block_numer, name):
        # run a javascript by the dev to get past events
        self.log.info('Gett past events for %s'%name)
        stdout = os.path.join(self.output, 'poller_%s.out'%name)
        stderr = os.path.join(self.output, 'poller_%s.err'%name)
        logout = os.path.join(self.output, 'poller_%s.log'%name)
        script = os.path.join(self.input, 'poller.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--address', '%s' % contract.address])
        args.extend(['--contract_abi', '%s' % contract.abi_path])
        args.extend(['--contract_abi', '%s' % contract.abi_path])
        args.extend(['--log_file', '%s' % logout])
        args.extend(['--from_block', '%s' % block_numer])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Completed task', timeout=30)
        return logout
