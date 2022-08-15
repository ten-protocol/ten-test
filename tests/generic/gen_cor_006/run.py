from ethsys.basetest import EthereumTest
from ethsys.contracts.erc20.obx import OBXCoin
from ethsys.contracts.guesser.guesser_token import GuesserToken
from ethsys.networks.factory import NetworkFactory


class PySysTest(EthereumTest):

    def execute(self):
        # connect to the network
        network = NetworkFactory.get_network(self)
        web3_deploy, deploy_account = network.connect_account1()
        web3_user, user_account = network.connect_account2()
        self.log.info('Deploying with account %s' % deploy_account.address)
        self.log.info('Playing with account %s' % user_account.address)

        # deploy the token contract
        self.log.info('Deploy the OBXCoin contract')
        erc20 = OBXCoin(self, web3_deploy)
        tx_receipt = network.transact(self, web3_deploy, erc20.contract, deploy_account, erc20.GAS)
        token_contract_address = tx_receipt.contractAddress
        token_contract = web3_deploy.eth.contract(address=token_contract_address, abi=erc20.abi)

        # deploy the game contract
        self.log.info('Deploy the Guessing game ')
        guesser = GuesserToken(self, web3_deploy, 5, token_contract_address)
        tx_receipt = network.transact(self, web3_deploy, guesser.contract, deploy_account, guesser.GAS)
        game_contract_address = tx_receipt.contractAddress
        game_contract = web3_deploy.eth.contract(address=game_contract_address, abi=guesser.abi)

        # transfer some tokens into the guessing account
        self.log.info('Transfer some tokens ')
        network.transact(self, web3_deploy, token_contract.functions.transfer(user_account.address, 200), deploy_account, erc20.GAS)

        # the user starts making guesses (first needs to approve the game to take tokens)
        token_contract_user = web3_user.eth.contract(address=token_contract_address, abi=erc20.abi)
        game_contract_user = web3_user.eth.contract(address=game_contract_address, abi=guesser.abi)

        for i in range(0,5):
            self.log.info('Guessing number as %d' % i)
            network.transact(self, web3_user, token_contract_user.functions.approve(game_contract_address, 1), user_account, guesser.GAS)
            network.transact(self, web3_user, game_contract_user.functions.attempt(i), user_account, guesser.GAS)

            self.log.info('Checking balances ...')
            prize = game_contract_user.functions.getBalance().call()
            if prize == 0:
                self.log.info('Game balance is zero so user guess the right number')
                self.log.info('User balance is %d' % token_contract_user.functions.balanceOf(user_account.address).
                              call({'from': user_account.address}))
                break
            else:
                self.log.info('Game balance is %d ' % game_contract_user.functions.getBalance().call())
