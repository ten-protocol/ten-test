from web3 import Web3
from pysys.constants import PASSED
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.utils.properties import Properties
from obscuro.test.contracts.erc20.minted_erc20 import MintedERC20Token
from obscuro.test.contracts.guesser.guesser_token import GuesserToken
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contracts
        network = NetworkFactory.get_network(self)
        web3_deploy, deploy_account = network.connect_account1(self)
        account2 = Web3().eth.account.privateKeyToAccount(Properties().account2pk())

        erc20 = MintedERC20Token(self, web3_deploy, 'OBXCoin', 'OBX', 1000000)
        erc20.deploy(network, deploy_account)
        network.transact(self, web3_deploy, erc20.contract.functions.transfer(account2.address, 200), deploy_account, erc20.GAS_LIMIT)

        guesser = GuesserToken(self, web3_deploy, 5, erc20.address)
        guesser.deploy(network, deploy_account)

        # the user starts making guesses
        web3, account = network.connect_account2(self)
        token = web3.eth.contract(address=erc20.address, abi=erc20.abi)
        game = web3.eth.contract(address=guesser.address, abi=guesser.abi)

        for i in range(0,6):
            self.log.info('Guessing number as %d' % i)
            network.transact(self, web3, token.functions.approve(guesser.address, 1), account, guesser.GAS_LIMIT)
            network.transact(self, web3, game.functions.attempt(i), account, guesser.GAS_LIMIT)

            self.log.info('Checking balances ...')
            prize = game.functions.getBalance().call()
            if prize == 0:
                self.log.info('Game balance is zero so user guessed the right number')
                self.log.info('User balance is %d' % token.functions.balanceOf(account.address).
                              call({'from': account.address}))
                self.addOutcome(PASSED)
                break
            else:
                self.log.info('Game balance is %d ' % game.functions.getBalance().call())

