import os
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import TransparentGuessGame


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect the players to the network
        network_1 = self.get_network_connection()
        network_2 = self.get_network_connection()
        web3_1, account_1 = network_1.connect_account1(self)
        web3_2, account_2 = network_2.connect_account2(self)

        # player 1 deploys the contract
        game_1 = TransparentGuessGame(self, web3_1)
        game_1.deploy(network_1, account_1)
        block_number = web3_1.eth.get_block_number()

        # player 2 transacts with the contract
        game_2 = TransparentGuessGame.clone(web3_2, account_2, game_1)
        target = game_2.contract.functions.guess
        for i in range(1,5): network_2.transact(self, web3_2, target(i), account_2, game_2.GAS_LIMIT)

        # both players should be able to get all events
        self.get_logs(network_1, game_1, block_number, '1')
        self.get_logs(network_2, game_2, block_number, '2')

    def get_logs(self, network, contract, block_numer, name):
        # run a javascript by the dev to get past events
        self.log.info('Get past events for %s'%name)
        stdout = os.path.join(self.output, 'poller_%s.out'%name)
        stderr = os.path.join(self.output, 'poller_%s.err'%name)
        logout = os.path.join(self.output, 'poller_%s.log'%name)
        script = os.path.join(self.input, 'poller.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--address', '%s' % contract.address])
        args.extend(['--contract_abi', '%s' % contract.abi_path])
        args.extend(['--log_file', '%s' % logout])
        args.extend(['--from_block', '%s' % block_numer])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Completed task', timeout=30)

        self.assertLineCount(file=logout, expr='Guessed event:', condition='==4')
        self.assertOrderedGrep(file=logout, exprList=['guessedNumber = %d' % d for d in range(1,5)])
        self.assertLineCount(file=logout, expr='Attempts event:', condition='==4')
        self.assertOrderedGrep(file=logout, exprList=['attempts = %d' % d for d in range(1,5)])