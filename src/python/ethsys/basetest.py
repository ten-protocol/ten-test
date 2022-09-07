import json, requests
from pysys.basetest import BaseTest
from ethsys.utils.properties import Properties


class EthereumTest(BaseTest):
    ONE_GIGA = 1000000000000000000
    OBX_TARGET = 100000 * ONE_GIGA
    OBX_THRESHOLD = 100 * ONE_GIGA
    TOKEN_TARGET = 50 * ONE_GIGA
    TOKEN_THRESHOLD = 5 * ONE_GIGA

    def __init__(self, descriptor, outsubdir, runner):
        """Call the parent constructor but set the mode to obscuro if non is set. """
        super().__init__(descriptor, outsubdir, runner)
        self.env = 'obscuro' if self.mode is None else self.mode

    def fund_obx(self, network, web3_user, user_account, web3_faucet, faucet_account, target=None, threshold=None):
        """Fund OBX in the L2 to a users account, either through the faucet server or direct from the account.

        Note this assumes the PK for the user is available i.e. we are able to check balances.
        """
        target = self.OBX_TARGET if target is None else target
        threshold = self.OBX_THRESHOLD if threshold is None else threshold
        if self.env in ['obscuro', 'obscuro.dev']:
            self.obx_from_faucet_server(web3_user, user_account, web3_faucet, faucet_account, threshold)
        else:
            self.obx_from_faucet_pk(network, web3_user, user_account, web3_faucet, faucet_account, target, threshold)

    def obx_from_faucet_server(self, web3_user, user_account, web3_faucet, faucet_account, threshold):
        """Allocates native OBX to a users account from the faucet server.
        """
        self.log.info('Running for native OBX token using faucet server')
        faucet_obx = web3_faucet.eth.get_balance(faucet_account.address)
        user_obx = web3_user.eth.get_balance(user_account.address)
        self.log.info('  L2 balances before;')
        self.log.info('    OBX Faucet balance = %d ' % faucet_obx)
        self.log.info('    OBX User balance   = %d ' % user_obx)

        if user_obx < threshold:
            headers = {'Content-Type': 'application/json'}
            data = {"address": user_account.address}
            response = requests.post(Properties().faucet_url(self.env), data=json.dumps(data), headers=headers)

            faucet_obx = web3_faucet.eth.get_balance(faucet_account.address)
            user_obx = web3_user.eth.get_balance(user_account.address)
            self.log.info('  L2 balances after;')
            self.log.info('    OBX Faucet balance = %d ' % faucet_obx)
            self.log.info('    OBX User balance   = %d ' % user_obx)

    def obx_from_faucet_pk(self, network, web3_user, user_account, web3_faucet, faucet_account, target=None, threshold=None):
        """Allocates native OBX to a users account from the faucet private key.
        """
        self.log.info('Running for native OBX token using faucet pk')
        faucet_obx = web3_faucet.eth.get_balance(faucet_account.address)
        deploy_obx = web3_user.eth.get_balance(user_account.address)
        self.log.info('  L2 balances before;')
        self.log.info('    OBX Faucet balance = %d ' % faucet_obx)
        self.log.info('    OBX User balance   = %d ' % deploy_obx)

        if deploy_obx < threshold:
            amount = (target - deploy_obx)
            self.log.info('Increase deployment account native OBX by %d ' % amount)

            # transaction from the faucet to the deployment account
            tx = {
                'nonce': web3_faucet.eth.get_transaction_count(faucet_account.address),
                'to': user_account.address,
                'value': amount,
                'gas': 4 * 720000,
                'gasPrice': 21000
            }
            tx_sign = faucet_account.sign_transaction(tx)
            tx_hash = network.send_transaction(self, web3_faucet, None, tx_sign)
            network.wait_for_transaction(self, web3_faucet, tx_hash)

            faucet_obx = web3_faucet.eth.get_balance(faucet_account.address)
            deploy_obx = web3_user.eth.get_balance(user_account.address)
            self.log.info('  Native OBX balances after;')
            self.log.info('    Faucet balance = %d ' % faucet_obx)
            self.log.info('    Deployment balance = %d ' % deploy_obx)

    def fund_token(self, network, token_name, token,
                      web3_user, user_account,
                      web3_deploy, deploy_account,
                      web3_faucet, faucet_account,
                      target=None, threshold=None):
        """Allocates ERC20 tokens from a token contract to a users account within that contract.

        This is a reallocation of tokens within a token contract to a particular user.
        """
        self.log.info('Running for token %s' % token_name)
        target = self.TOKEN_TARGET if target is None else target
        threshold = self.TOKEN_THRESHOLD if threshold is None else threshold

        deploy_balance = token.functions.balanceOf(deploy_account.address).call()
        user_balance = token.functions.balanceOf(user_account.address).call({'from': user_account.address})
        faucet_obx_balance = web3_faucet.eth.get_balance(faucet_account.address)
        deploy_obx_balance = web3_deploy.eth.get_balance(deploy_account.address)
        user_obx_balance = web3_user.eth.get_balance(user_account.address)
        self.log.info('  L2 balances before;')
        self.log.info('    OBX Faucet balance = %d ' % faucet_obx_balance)
        self.log.info('    OBX Deploy account balance = %d ' % deploy_obx_balance)
        self.log.info('    OBX User balance = %d ' % user_obx_balance)
        self.log.info('    %s Deploy account balance = %d ' % (token_name, deploy_balance))
        self.log.info('    %s User account balance = %d ' % (token_name, user_balance))

        if user_balance < threshold:
            amount = target - user_balance
            self.log.info('Increase user account token %s by %d ' % (token_name, amount))

            network.transact(self, web3_deploy, token.functions.transfer(user_account.address, amount),
                             deploy_account, 7200000)

            deploy_balance = token.functions.balanceOf(deploy_account.address).call()
            user_balance = token.functions.balanceOf(user_account.address).call({'from': user_account.address})
            faucet_obx_balance = web3_faucet.eth.get_balance(faucet_account.address)
            deploy_obx_balance = web3_deploy.eth.get_balance(deploy_account.address)
            user_obx_balance = web3_user.eth.get_balance(user_account.address)
            self.log.info('  L2 balances after;')
            self.log.info('    OBX Faucet balance = %d ' % faucet_obx_balance)
            self.log.info('    OBX Deploy account balance = %d ' % deploy_obx_balance)
            self.log.info('    OBX User balance = %d ' % user_obx_balance)
            self.log.info('    %s Deploy account balance = %d ' % (token_name, deploy_balance))
            self.log.info('    %s User account balance = %d ' % (token_name, user_balance))