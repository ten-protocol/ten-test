from web3.exceptions import TimeExhausted
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        contract = Storage(self, web3, 0)
        contract.deploy(network, account)

        # estimate gas required to call the add_once contract function
        estimate_gas = contract.contract.functions.store(1).estimate_gas()
        self.log.info("Estimate gas:    %d", estimate_gas)

        # submit the transaction to the function call with decreasing gas supplied
        # if the transaction times out, use the same nonce to replace it and supply the
        # full gas amount
        for i in [0.9, 0.8, 0.6, 0.4, 0.1]:
            self.log.info("")
            self.log.info(" **** Submitting with fractional lower gas of %f **** ", i)
            use_gas = int(i * estimate_gas)
            nonce = self.nonce_db.get_next_nonce(self, web3, account.address, self.env)
            self.log.info("Transact gas:    %d", use_gas)
            try:
                self.log.info('Submitting the transaction with lower gas than the estimate')
                self.submit(account, contract, nonce, web3, use_gas)
            except TimeExhausted as e:
                self.log.info('Time exhausted so increasing the gas to the estimate')
                self.submit(account, contract, nonce, web3, estimate_gas)
            except ValueError as e:
                self.log.info(e['message'])

    def submit(self, account, contract, nonce, web3, gas):
        build_tx = contract.contract.functions.store(1).build_transaction(
            { 'nonce':nonce, 'gasPrice':web3.eth.gas_price, 'gas':gas, 'chainId':web3.eth.chain_id }
        )
        signed_tx = account.sign_transaction(build_tx)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash.hex(), timeout=10)
        if tx_receipt.status == 1:
            self.log.info('Transaction successful with block hash %s', tx_receipt.blockHash.hex())
            self.nonce_db.update(account.address, self.env, nonce, 'CONFIRMED')
        else:
            try:
                web3.eth.call(build_tx, block_identifier=tx_receipt.blockNumber)
            except Exception as e:
                self.log.error('Replay call: %s', e)
