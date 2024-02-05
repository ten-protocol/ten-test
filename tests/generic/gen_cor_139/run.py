import secrets
from ten.test.basetest import GenericNetworkTest
from ten.test.utils.properties import Properties


class PySysTest(GenericNetworkTest):
    SEND_AMOUNT = 1

    def execute(self):
        network = self.get_network_connection()
        web3_fund, account_fund = self.network_funding.connect(self, Properties().fundacntpk(), check_funds=False)
        web3_send, account_send = network.connect(self, private_key=secrets.token_hex(32), check_funds=False)
        web3_recv, account_recv = network.connect(self, private_key=secrets.token_hex(32), check_funds=False)

        # how much will it cost in wei to transfer some funds regardless of the amount
        gas_price = web3_fund.eth.gas_price
        tx = {'to': account_send.address, 'value': 1, 'gasPrice': gas_price}
        gas_estimate = web3_fund.eth.estimate_gas(tx)
        transfer_cost = gas_estimate * gas_price
        self.log.info('Transfer cost:    %d', transfer_cost)

        # fund the receiving account with this much money plus one extra wei
        tx = {'to': account_send.address, 'value': 1+transfer_cost, 'gasPrice': gas_price, 'gas':gas_estimate}
        network.tx(self, web3_fund, tx, account_fund, timeout=10)
        self.log.info('Sender balance:   %d', web3_send.eth.get_balance(account_send.address))

        # send one wei to the receiver which should drain the account
        tx = {'to': account_recv.address, 'value': 1, 'gasPrice': gas_price, 'gas':gas_estimate}
        network.tx(self, web3_send, tx, account_send, timeout=10)
        self.log.info('Sender balance: %d', web3_send.eth.get_balance(account_send.address))
        self.log.info('Receiver balance: %d', web3_recv.eth.get_balance(account_recv.address))

    def validate(self):
        pass
