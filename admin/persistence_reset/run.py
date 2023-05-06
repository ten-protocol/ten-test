from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        PKS = [
            Properties().funded_account_pk(self.env),
            Properties().account1_1pk(), Properties().account2_1pk(), Properties().account3_1pk(), Properties().account4_1pk(),
            Properties().account1_2pk(), Properties().account2_2pk(), Properties().account3_2pk(), Properties().account4_2pk(),
            Properties().account1_3pk(), Properties().account2_3pk(), Properties().account3_3pk(), Properties().account4_3pk()
        ]

        self.log.info('Removing entries for environment %s' % self.env)
        self.nonce_db.delete_environment(self.env)

        network = NetworkFactory.get_network(self)
        for pk in PKS:
            web3, account = network.connect(self, pk, check_funds=False)
            count = web3.eth.get_transaction_count(account.address)  # count is what the next would be
            self.log.info('Account %s transaction count is %d' % (account.address, count))
            if count > 0:
                self.log.info('Account %s updating last persisted nonce to %d' % (account.address, count-1))
                self.nonce_db.insert(account.address, self.env, count-1, 'RESET')



