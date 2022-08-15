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

        # deploy the contract
        self.log.info('Deploy the Guessing game ')
        guesser = GuesserToken(self, web3_deploy, 10, token_contract_address)
        tx_receipt = network.transact(self, web3_deploy, guesser.contract, deploy_account, guesser.GAS)
        game_contract_address = tx_receipt.contractAddress
        game_contract = web3_deploy.eth.contract(address=game_contract_address, abi=guesser.abi)

