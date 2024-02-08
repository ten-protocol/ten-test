import secrets
from pysys.constants import PASSED, FAILED
from web3.exceptions import TimeExhausted
from ten.test.basetest import GenericNetworkTest
from ten.test.utils.properties import Properties


class PySysTest(GenericNetworkTest):

    def execute(self):
        # get the network, and connect two ephemeral accounts for the test
        network = self.get_network_connection()
        ps_sender = secrets.token_hex(32)
        pk_receiver = secrets.token_hex(32)
        web3, _ = self.network_funding.connect(self, Properties().fundacntpk(), check_funds=False)
        web3_send, account_send = network.connect(self, private_key=ps_sender, check_funds=False)
        web3_recv, account_recv = network.connect(self, private_key=pk_receiver, check_funds=False)

        # determine how much will it cost in wei to transfer funds regardless of the amount, give the sender
        # just enough funds for the cost with no residual for the amount to actually be sent
        gas_price = web3.eth.gas_price
        tx = {'to': account_recv.address, 'value': 1, 'gasPrice': gas_price}
        gas_estimate = web3.eth.estimate_gas(tx)
        transfer_cost = gas_estimate * gas_price
        self.log.info('Transfer cost:    %d', transfer_cost)
        self.distribute_native(account_send, web3_send.from_wei(transfer_cost, 'ether'), verbose=False)
        self.log.info('Sender balance:   %d', web3_send.eth.get_balance(account_send.address))

        # try to make the transaction and when it fails increase the funds and replace
        self.log.info(' ')
        self.log.info('Sending transaction with funds to cover the gas cost, but not the funds to be sent')
        tx_hash, tx_receipt = self.submit(web3_send, account_send, account_recv.address, 1, gas_price, gas_estimate)
        if tx_receipt is None:
            self.log.info('Transaction timed out, adding funds to cover the gas cost and the amount being sent')
            self.distribute_native(account_send, web3_send.from_wei(1, 'ether'), verbose=False)
            self.log.info('Sender balance:   %d', web3_send.eth.get_balance(account_send.address))

            self.log.info('Attempt to wait on the original tx hash now the account has funds')
            try:
                web3.eth.wait_for_transaction_receipt(tx_hash, timeout=15)
                self.log.info('Unexpected behaviour in that the tx has been picked up and mined')
                self.addOutcome(FAILED)
            except TimeExhausted as e:
                self.log.info('Waiting did not work as expected so resending the transaction')
                tx_hash, tx_receipt = self.submit(web3_send, account_send, account_recv.address, 1, gas_price, gas_estimate)
                if tx_receipt is None:
                    self.log.info('Unexpected behaviour in that the tx did not go through')
                    self.addOutcome(FAILED)
                else:
                    self.log.info('Expected behaviour in that the tx has now gone through')
                    self.addOutcome(PASSED)
        else:
            self.log.info('Unexpected behaviour in that the tx has been picked up and mined')
            self.addOutcome(FAILED)

        self.log.info(' ')
        self.log.info('Sender balance: %d', web3_send.eth.get_balance(account_send.address))
        self.log.info('Receiver balance: %d', web3_recv.eth.get_balance(account_recv.address))
        self.assertTrue(web3_recv.eth.get_balance(account_recv.address) == 1)

    def submit(self, web3, account, to_address, value, gas_price, gas_estimate, nonce=0):
        tx = {'to': to_address, 'value': value, 'gasPrice': gas_price, 'gas': gas_estimate,
              'nonce': nonce, 'chainId': web3.eth.chain_id}
        signed_tx = account.sign_transaction(tx)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = None
        try:
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash.hex(), timeout=15)
        except TimeExhausted as e:
            self.log.error(e)
        except ValueError as e:
            self.log.error(e)
        finally:
            return (tx_hash, tx_receipt)
