from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):
    ONE_GIGA = 1000000000000000000
    OBX_TARGET = 1000 * ONE_GIGA
    OBX_THRESHOLD = 1 * ONE_GIGA

    def execute(self):
        # connect to the L2 network
        network = Obscuro
        web3_deploy, deploy_account = network.connect(Properties().funded_deployment_account_pk(self.env), network.HOST,
                                                      network.PORT)
        web3_faucet, faucet_account = network.connect(Properties().faucet_pk(self.env), network.HOST,
                                                      network.ACCOUNT2_PORT)

        faucet_obx = web3_faucet.eth.get_balance(faucet_account.address)
        deploy_obx = web3_deploy.eth.get_balance(deploy_account.address)
        self.log.info('  Native OBX balances before;')
        self.log.info('    Faucet balance = %d ' % faucet_obx)
        self.log.info('    Deployment balance = %d ' % deploy_obx)

        if deploy_obx < self.OBX_THRESHOLD:
            amount = (self.OBX_TARGET - deploy_obx)
            self.log.info('Increase deployment account native OBX by %d ' % amount)

            # transaction from the faucet to the deployment account
            tx = {
                'nonce': web3_faucet.eth.get_transaction_count(faucet_account.address),
                'to': deploy_account.address,
                'value': amount,
                'gas': 4 * 720000,
                'gasPrice': 21000
            }
            tx_sign = faucet_account.sign_transaction(tx)
            tx_hash = network.send_transaction(self, web3_faucet, None, tx_sign)
            network.wait_for_transaction(self, web3_faucet, tx_hash)

            faucet_obx = web3_faucet.eth.get_balance(faucet_account.address)
            deploy_obx = web3_deploy.eth.get_balance(deploy_account.address)
            self.log.info('  Native OBX balances after;')
            self.log.info('    Faucet balance = %d ' % faucet_obx)
            self.log.info('    Deployment balance = %d ' % deploy_obx)

