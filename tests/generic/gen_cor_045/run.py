import os
from web3 import Web3
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.game.token import Token
from obscuro.test.contracts.game.game import Game
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties
from obscuro.test.helpers.log_subscriber import AllEventsLogSubscriber

class PySysTest(GenericNetworkTest):
    GENERAL_SUB = False

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self)
        web3_usr, account_usr = network.connect(self, Properties().gg_endusr_pk())
        web3_dev, account_dev = network.connect(self, Properties().gg_appdev_pk())

        token = Token(self, web3_dev)
        token.deploy(network, account_dev)

        game = Game(self, web3_dev, 10, token.address)
        game.deploy(network, account_dev)

        # run a background generic script if needed
        if self.GENERAL_SUB:
            subscriber = AllEventsLogSubscriber(self, network, game,
                                                stdout='subscriber1.out',
                                                stderr='subscriber1.err')
            subscriber.run(Properties().gg_endusr_pk(), network.connection_url(), network.connection_url(True))

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'subscriber2.out')
        stderr = os.path.join(self.output, 'subscriber2.err')
        script = os.path.join(self.input, 'listener.js')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--network_ws', '%s' % network.connection_url(web_socket=True)])
        args.extend(['--erc_address', '%s' % token.address])
        args.extend(['--erc_abi', '%s' % token.abi_path])
        args.extend(['--game_address', '%s' % game.address])
        args.extend(['--game_abi', '%s' % game.abi_path])
        args.extend(['--pk_address', '%s' % Web3().eth.account.privateKeyToAccount(Properties().gg_endusr_pk()).address])
        if self.is_obscuro(): args.extend(['--pk_to_register', '%s' % Properties().gg_endusr_pk()])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        # approve the game to spend tokens on behalf of the user
        token_player = web3_usr.eth.contract(address=token.address, abi=token.abi)
        network.transact(self, web3_usr, token_player.functions.approve(game.address, Web3().toWei(10, 'ether')), account_usr, game.GAS_LIMIT)

        # play the game
        game_player = web3_usr.eth.contract(address=game.address, abi=game.abi)
        for i in range(0,9):
            allowance = token_player.functions.allowance(account_usr.address, game.address).call({"from":account_usr.address})
            balance = token_player.functions.balanceOf(account_usr.address).call({"from":account_usr.address})
            self.log.info('Allowance is %.3f' % Web3().fromWei(allowance, 'ether'))
            self.log.info('Balance is %.3f' % Web3().fromWei(balance, 'ether'))
            network.transact(self, web3_usr, game_player.functions.attempt(i), account_usr, game.GAS_LIMIT)
            self.wait(float(self.block_time)*1.1)

