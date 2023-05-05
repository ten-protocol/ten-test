import re
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.gas import GasConsumerBalance
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        contract = GasConsumerBalance(self, web3)
        contract.deploy(network, account)

        est_1 = contract.contract.functions.get_balance().estimate_gas()
        self.log.info("Estimate get_balance:    %d" % est_1)

        nonce = self.nonce_db.get_next_nonce(self, web3, account.address, self.env)
        build_tx = contract.contract.functions.get_balance().buildTransaction(
            {
                'nonce': nonce,
                'gasPrice': web3.eth.gas_price, # the price we are willing to pay per gas unit (dimension is gwei)
                'gas': int(est_1 / 2),          # max gas units prepared to pay (dimension is computational units)
                'chainId': web3.eth.chain_id
            }
        )
        signed_tx = account.sign_transaction(build_tx)
        try:
            web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        except Exception as e:
            self.log.error('Exception type: %s' % type(e))
            self.log.error('Exception message: %s' % e.args[0]['message'])
            regex = re.compile('intrinsic gas too low', re.M)
            self.assertTrue(regex.search(e.args[0]['message']) is not None)


