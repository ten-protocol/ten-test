import os
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import Game


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway, and deploy the game contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        game = Game(self, web3)
        game.deploy(network, account)
        block_number = web3.eth.get_block_number()

        # get a session key for this userid and fund it
        sk = self.get_session_key(network.connection_url())
        tx = {'to': sk, 'value': web3.to_wei(0.01, 'ether'), 'gasPrice': web3.eth.gas_price}
        tx['gas'] = web3.eth.estimate_gas(tx)
        network.tx(self, web3, tx, account)
        self.log.info('  Session key: %s' % sk)
        self.log.info('  Balance of session key: %d' % web3.eth.get_balance(sk))
        self.log.info('  Balance of account1:    %d' % web3.eth.get_balance(account.address))

        # activate the session key now that we have funded it
        self.activate_session_key(network.connection_url())

        # transact using the session key and get the logs
        for i in range(1,5): network.transact_unsigned(self, web3, game.contract.functions.guess(i), sk, game.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)
        self.get_logs(network, game, block_number)

        # return the funds and deactivate
        tx = {'to': account.address, 'gasPrice': web3.eth.gas_price}
        tx['gas'] = web3.eth.estimate_gas(tx)
        tx['value'] = web3.eth.get_balance(sk) - (tx['gas'] * web3.eth.gas_price)
        network.tx_unsigned(self, web3, tx, sk)
        self.deactivate_session_key(network.connection_url())

    def get_logs(self, network, contract, block_numer):
        # run a javascript by account1 to get past events
        self.log.info('Get past events')
        stdout = os.path.join(self.output, 'poller.out')
        stderr = os.path.join(self.output, 'poller.err')
        logout = os.path.join(self.output, 'poller.log')
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