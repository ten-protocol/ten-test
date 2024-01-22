from hexbytes import HexBytes
from web3.exceptions import TimeExhausted
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage

class TransactionFailed(Exception):
    pass

class PySysTest(GenericNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        contract = Storage(self, web3, 0)
        contract.deploy(network, account)

        # estimate gas required to call the add_once contract function
        estimate_gas = contract.contract.functions.store(1).estimate_gas()
        self.log.info("Estimate gas:    %d", estimate_gas)

        # submit at the estimate and then from the transaction work out the intrinsic gas
        nonce = self.nonce_db.get_next_nonce(self, web3, account.address, self.env)
        tx_receipt = self.submit(account, contract, web3, nonce, estimate_gas)
        intrinsic_gas = self.calculate_intrinsic_gas(web3, tx_receipt.transactionHash)

        # submit at the intrinsic gas
        nonce = self.nonce_db.get_next_nonce(self, web3, account.address, self.env)
        self.submit(account, contract, web3, nonce, intrinsic_gas)

    def submit(self, account, contract, web3, nonce, gas_limit):
        tx_receipt = None
        build_tx = contract.contract.functions.store(1).build_transaction(
            {
                'nonce': nonce,
                'gasPrice': web3.eth.gas_price,
                'gas': gas_limit,
                'chainId': web3.eth.chain_id
            })
        signed_tx = account.sign_transaction(build_tx)

        # send and wait for the transaction result (mined, timed out or rejected)
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash.hex(), timeout=10)

            # 1 - was mined and was either successful or failed
            if tx_receipt.status == 1:
                self.log.info('Transaction successful')
                self.nonce_db.update(account.address, self.env, nonce, 'CONFIRMED')
            else:
                self.log.info('Transaction failed')
                try:
                    web3.eth.call(build_tx, block_identifier=tx_receipt.blockNumber)
                except Exception as e:
                    self.log.error('Replay call: %s', e)

        # 2- was not mined and likely still in the mempool waiting
        except TimeExhausted as e:
            self.log.error(e)

        # 3 - was not mined and was reject from the mempool
        except ValueError as e:
            self.log.error(e)

        finally:
            return tx_receipt

    def calculate_intrinsic_gas(self, web3, tx_hash):
        tx = web3.eth.get_transaction(tx_hash)

        hex_data = HexBytes(tx['input'])
        self.log.info('Input hex data is %s', hex_data.hex())
        zero_count = sum(1 for byte in hex_data if byte == 0)
        non_zero_count = sum(1 for byte in hex_data if byte != 0)

        self.log.info('Data size is %d', len(hex_data))
        self.log.info('Non zero count is %d', non_zero_count)
        self.log.info('Zero count is %d', zero_count)

        intrinsic_gas = 21000 + (16*non_zero_count) + (4*zero_count)
        self.log.info('Intrinsic gas is %d', intrinsic_gas)
        return intrinsic_gas
