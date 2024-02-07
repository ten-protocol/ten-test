import secrets, os
from web3.exceptions import TimeExhausted
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        # get the network and two ephemeral accounts to send and receive funds at the threshold
        # note we only need the funding web3 connection to estimate gas for the transfer
        network = self.get_network_connection()
        web3, _ = self.network_funding.connect(self, Properties().fundacntpk(), check_funds=False)

        ps_sender = secrets.token_hex(32)
        pk_receiver = secrets.token_hex(32)
        web3_send, account_send = network.connect(self, private_key=ps_sender, check_funds=False)
        web3_recv, account_recv = network.connect(self, private_key=pk_receiver, check_funds=False)

        # how much will it cost in wei to transfer some funds regardless of the amount
        gas_price = web3.eth.gas_price
        tx = {'to': account_recv.address, 'value': 1, 'gasPrice': gas_price}
        gas_estimate = web3.eth.estimate_gas(tx)
        transfer_cost = gas_estimate * gas_price
        target_funds = 1 + transfer_cost
        self.log.info('Transfer cost:    %d', transfer_cost)

        # kick off a bulk loader in the background to ensure the mempool is full and batches have more than one tx
        funds_needed = 5 * (64 * transfer_cost)
        self.run_client(network, funds_needed, txs=16)

        # top up with the target funds amount, which is 1 wei more than the cost of the transfer, and then
        # try and send the funds. If it fails, top up some more and then wait
        for i in range(0, 10):
            self.log.info(' ')
            self.log.info('Running an iteration to send with marginal amounts')
            balance = web3_send.eth.get_balance(account_send.address)
            if balance < target_funds:
                self.log.info('Topping up senders account with %d', target_funds - balance)
                self.distribute_native(account_send, web3_send.from_wei(target_funds - balance, 'ether'), verbose=False)
                self.log.info('Sender balance:   %d', web3_send.eth.get_balance(account_send.address))

            tx_hash, tx_receipt = self.submit(web3_send, account_send, account_recv.address, 1, gas_price, gas_estimate)
            if tx_receipt is None:
                self.log.info('Transaction timed out sending more funds')
                self.log.info('Before balance:   %d', web3_send.eth.get_balance(account_send.address))
                self.distribute_native(account_send, web3_send.from_wei(transfer_cost, 'ether'), verbose=False)
                self.log.info('After balance:   %d', web3_send.eth.get_balance(account_send.address))
                self.log.info('Waiting on the transaction receipt again')
                web3_send.eth.wait_for_transaction_receipt(tx_hash.hex(), timeout=30)
                self.log.info('Transaction successful')
                self.log.info('Transaction count is %d', self.scan_get_total_transaction_count())
            else:
                self.log.info('Transaction successful')

        self.log.info(' ')
        self.log.info('Sender balance: %d', web3_send.eth.get_balance(account_send.address))
        self.log.info('Receiver balance: %d', web3_recv.eth.get_balance(account_recv.address))
        self.assertTrue(web3_recv.eth.get_balance(account_recv.address) == 10)

    def submit(self, web3, account, to_address, value, gas_price, gas_estimate):
        tx = {'to': to_address, 'value': value, 'gasPrice': gas_price, 'gas': gas_estimate}
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
            return (tx_hash, tx_receipt)


