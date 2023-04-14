import secrets, random
from web3 import Web3
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):
    ITERATIONS = 5000

    def execute(self):
        # connect to the network
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # a list of recipient accounts
        accounts = [Web3().eth.account.privateKeyToAccount(x).address for x in [secrets.token_hex()]*25]

        # bulk load transactions to the accounts, and wait for the last
        self.log.info('Creating transactions')
        txs = []
        for i in range(0, self.ITERATIONS):
            recip = random.choice(accounts)
            nonce = network.get_next_nonce(self, web3, account, persist_nonce=True, log=False)
            tx_sign = self.send_funds(network, web3, account, nonce, recip, 0.00000001)
            txs.append((tx_sign, nonce))

        self.log.info('Sending transactions')
        nonce = None
        tx_hash = None
        for tx in txs:
            nonce = tx[1]
            tx_hash = network.send_transaction(self, web3, nonce, account, tx[0], persist_nonce=True, log=False)

        self.log.info('Waiting for last transaction')
        network.wait_for_transaction(self, web3, nonce, account, tx_hash, persist_nonce=True)

    def send_funds(self, network, web3, account, nonce, address, amount):
        tx = {'nonce': nonce,
              'to': address,
              'value': web3.toWei(amount, 'ether'),
              'gas': 4 * 720000,
              'gasPrice': 21000,
              'chainId': network.chain_id()
              }
        return network.sign_transaction(self, tx, nonce, account, persist_nonce=True)
