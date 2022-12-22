from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        PKS = [
            Properties().account1pk(),
            Properties().account2pk(),
            Properties().account3pk(),
            Properties().account4pk(),
            Properties().l2_funded_account_pk(self.env)
        ]

        for pk in PKS:
            account = Web3().eth.account.privateKeyToAccount(pk)
            self.log.info('Removing entries for address %s' % account.address)
            self.nonce_db.delete(account.address, self.env)

