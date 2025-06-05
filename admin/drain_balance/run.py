from pysys.constants import BLOCKED
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):
    RECV_AD = None  # the receiver address
    SEND_PK = None  # the sender private key
    REMAIN = 10  # balance to remain

    def execute(self):
        # receiver address and sender pk must be supplied at run time
        if self.RECV_AD is None or self.SEND_PK is None:
            self.addOutcome(BLOCKED, abortOnError=True, outcomeReason='Receiver address and sender pk must be supplied')

        # connect to the network on the L1
        network = self.get_l1_network_connection(self.env)
        web3, account = network.connect(self, private_key=self.SEND_PK, check_funds=False)

        # get the balance of the sender and if greater than the amount to be left remaining transfer the excess
        balance = web3.eth.get_balance(account.address)
        threshold = web3.to_wei(self.REMAIN, 'ether')
        amount = balance - threshold
        self.log.info('Sender account balance %.9f ETH', web3.from_wei(balance, 'ether'))
        if balance - threshold > 0:
            self.log.info('Draining %.9f from the sender account', web3.from_wei(amount, 'ether'))
            self.send(network, web3, account, self.RECV_AD, amount)

    def send(self, network, web3, account, address, amount):
        gas_price = web3.eth.gas_price
        gas_estimate = web3.eth.estimate_gas(
            {'to': address, 'value': amount, 'gasPrice': gas_price, 'chainId': web3.eth.chain_id})
        self.log.info('Gas price   : %d WEI', gas_price)
        self.log.info('Gas estimate: %d WEI', gas_estimate)
        self.log.info('Total Cost  : %.9f ETH', web3.from_wei(gas_price * gas_estimate, 'ether'))
        tx = {
            'to': address,
            'value': amount - gas_estimate,
            'gas': gas_estimate,
            'gasPrice': web3.eth.gas_price,
            'chainId': web3.eth.chain_id
        }
        return network.tx(self, web3, tx, account, persist_nonce=False, timeout=120, txstr='value transfer')
