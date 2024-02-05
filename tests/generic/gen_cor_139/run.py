import secrets
from web3.exceptions import TimeExhausted
from ten.test.basetest import GenericNetworkTest
from ten.test.utils.properties import Properties


class PySysTest(GenericNetworkTest):

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

        # fund the receiving account with this much money plus one extra wei, and send one wei to the receiver
        # should the transaction time out, resend on the same nonce but increase the funds of the sender
        self.log.info('Distribute funds to the sender account')
        self.distribute_native(account_send, web3_send.from_wei(1+transfer_cost, 'ether'), verbose=False)
        self.log.info('Sender balance:   %d', web3_send.eth.get_balance(account_send.address))

        while True:
            tx_receipt = self.submit(web3_send, account_send, account_recv.address, 1, gas_price, gas_estimate)
            if tx_receipt is None:
                self.log.info('Transaction timed out sending more funds')
                self.distribute_native(account_send, web3_send.from_wei(transfer_cost, 'ether'), verbose=False)
                self.log.info('Sender balance:   %d', web3_send.eth.get_balance(account_send.address))
            else:
                self.log.info('Transaction successful')
                break

        self.log.info(' ')
        self.log.info('Sender balance: %d', web3_send.eth.get_balance(account_send.address))
        self.log.info('Receiver balance: %d', web3_recv.eth.get_balance(account_recv.address))

    def submit(self, web3, account, to_address, value, gas_price, gas_estimate):
        tx = {'to': to_address, 'value': value, 'gasPrice': gas_price, 'gas':gas_estimate}
        nonce = web3.eth.get_transaction_count(account.address)
        self.log.info('Sender nonce:     %d', nonce)
        tx['nonce'] = nonce
        tx['chainId'] = web3.eth.chain_id
        signed_tx = account.sign_transaction(tx)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = None
        try:
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash.hex(), timeout=10)
        except TimeExhausted as e:
            self.log.error(e)
        except ValueError as e:
            self.log.error(e)
        finally:
            return tx_receipt

