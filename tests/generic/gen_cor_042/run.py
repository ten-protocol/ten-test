from pysys.constants import PASSED
from obscuro.test.basetest import EthereumTest
from obscuro.test.utils.properties import Properties
from obscuro.test.utils.keys import pk_to_account
from obscuro.test.contracts.erc20.obx import OBXCoin
from obscuro.test.contracts.guesser.guesser_token import GuesserToken
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(EthereumTest):
    WEBSOCKET = False

    def execute(self):
        # deployment of contracts
        network = NetworkFactory.get_network(self.env)
        web3_deploy, deploy_account = network.connect_account1(self, web_socket=self.WEBSOCKET)

        erc20 = OBXCoin(self, web3_deploy)
        erc20.deploy(network, deploy_account)
        erc20.transfer(network, pk_to_account(Properties().account2pk()).address, 200)

        guesser = GuesserToken(self, web3_deploy, 5, erc20.contract_address)
        guesser.deploy(network, deploy_account)

        # the user starts making guesses
        web3, account = network.connect_account2(self)
        token = web3.eth.contract(address=erc20.contract_address, abi=erc20.abi)
        game = web3.eth.contract(address=guesser.contract_address, abi=guesser.abi)

        for i in range(0,2):
            self.log.info('Guessing number as %d' % i)
            network.transact(self, web3, token.functions.approve(guesser.contract_address, 1), account, guesser.GAS)
            network.transact(self, web3, game.functions.attempt(i), account, guesser.GAS)

            self.log.info('Checking balances ...')
            prize = game.functions.getBalance().call()
            if prize == 0:
                self.log.info('Game balance is zero so user guess the right number')
                self.log.info('User balance is %d' % token.functions.balanceOf(account.address).
                              call({'from': account.address}))
                self.addOutcome(PASSED)
                break
            else:
                self.log.info('Game balance is %d ' % game.functions.getBalance().call())
