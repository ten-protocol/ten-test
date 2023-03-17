from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.contracts.payable import ReceiveEther, SendEther


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # deploy the contracts
        rcv_eth = ReceiveEther(self, web3)
        rcv_eth.deploy(network, account)

        snd_eth = SendEther(self, web3)
        snd_eth.deploy(network, account)

    def send(self, network, web3, account, address, amount):
        nonce = network.get_next_nonce(self, web3, account, False)
        tx = {
            'chainId': network.chain_id(),
            'nonce': nonce,
            'to': address,
            'value': web3.toWei(amount, 'ether'),
            'gas': 4*21000,
            'gasPrice': web3.eth.gas_price
        }
        tx_sign = account.sign_transaction(tx)
        tx_hash = network.send_transaction(self, web3, nonce, account, tx_sign, False)
        network.wait_for_transaction(self, web3, nonce, account, tx_hash, False)