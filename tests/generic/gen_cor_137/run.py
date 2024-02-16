import secrets
from web3 import Web3
from hexbytes import HexBytes
from web3.exceptions import TimeExhausted
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deploy the contract as account 1
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        contract = Storage(self, web3, 0)
        contract.deploy(network, account)

        # interact with the contract as an ephemeral account
        private_key = secrets.token_hex(32)
        self.distribute_native(Web3().eth.account.from_key(private_key), network.ETH_ALLOC_EPHEMERAL)
        web3, account = network.connect(self, private_key=private_key, check_funds=False)
        contract = Storage.clone(web3, account, contract)

        # estimate gas required to call the add_once contract function
        estimate_gas = contract.contract.functions.store(1).estimate_gas()

        # submit at the estimate and then from the transaction work out the intrinsic gas
        _, tx_receipt = self.submit(account, contract, web3, 0, estimate_gas)
        intrinsic_gas = self.calculate_intrinsic_gas(web3, tx_receipt.transactionHash)

        # submit at lower than the intrinsic gas
        result, _ = self.submit(account, contract, web3, 1, int(0.9*intrinsic_gas))
        self.assertTrue(result == 4)

    def submit(self, account, contract, web3, nonce, gas_limit):
        self.log.info('Submitting transaction with gas_limit of %d', gas_limit)
        result = None
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

            # 1 - was mined and successful
            if tx_receipt.status == 1:
                self.log.info('Transaction successful')
                result = 1

            # 2 - was mined and failed
            else:
                self.log.info('Transaction failed')
                result = 2
                try:
                    web3.eth.call(build_tx, block_identifier=tx_receipt.blockNumber)
                except Exception as e:
                    self.log.error('Replay call: %s', e)

        # 3 - was not mined and likely still in the mem pool waiting
        except TimeExhausted as e:
            result = 3
            self.log.info('Transaction timed out')
            self.log.error(e)

        # 4 - was not mined and was rejected from the mem pool
        except ValueError as e:
            result = 4
            self.log.info('Transaction value error')
            self.log.error(e)

        finally:
            return result, tx_receipt

    def calculate_intrinsic_gas(self, web3, tx_hash):
        tx = web3.eth.get_transaction(tx_hash)
        hex_data = HexBytes(tx['input'])
        zero_count = sum(1 for byte in hex_data if byte == 0)
        non_zero_count = sum(1 for byte in hex_data if byte != 0)
        intrinsic_gas = 21000 + (16*non_zero_count) + (4*zero_count)
        self.log.info('Intrinsic gas is calculated to be %d', intrinsic_gas)
        return intrinsic_gas
