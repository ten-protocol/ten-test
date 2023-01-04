from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        PKS = [
            Properties().account1pk(),
            Properties().account2pk(),
            Properties().account3pk(),
            Properties().account4pk(),
            Properties().distro_account_pk(self.env)
        ]

        self.log.info('Removing entries for environment %s' % self.env)
        self.nonce_db.delete_environment(self.env)

        network = NetworkFactory.get_network(self.env)
        for pk in PKS:
            web3, account = network.connect(self, pk)
            count = web3.eth.get_transaction_count(account.address)  # count is what the next would be
            if count > 0:                                            # if zero there aren't any transactions, store last
                self.log.info('Updating last persisted nonce for %s to %d' % (account.address, count-1))
                self.nonce_db.insert(account.address, self.env, count-1, 'RESET')


