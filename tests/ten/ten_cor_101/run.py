from pysys.constants import PASSED, FAILED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway and deploy the storage contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # get a session key for this connection and fund it
        sk = self.get_session_key(network.connection_url())

        self.log.info('  Balance of session key: %d' % web3.eth.get_balance(sk))
        self.log.info('  Balance of account1:    %d' % web3.eth.get_balance(account.address))
        tx = {'to': sk, 'value': web3.to_wei(0.01, 'ether'), 'gasPrice': web3.eth.gas_price, 'chainId': web3.eth.chain_id}
        tx['gas'] = web3.eth.estimate_gas(tx)
        network.tx(self, web3, tx, account)
        balance_before = web3.eth.get_balance(sk)
        self.log.info('  Balance of session key: %d' % web3.eth.get_balance(sk))
        self.log.info('  Balance of account1:    %d' % web3.eth.get_balance(account.address))

        # activate the session key now that we have funded it
        self.activate_session_key(network.connection_url())

        # transact using the session key
        network.transact_unsigned(self, web3, storage.contract.functions.store(2), sk, storage.GAS_LIMIT)
        call_value = storage.contract.functions.retrieve().call()
        balance_after1 = web3.eth.get_balance(sk)
        self.log.info('  Call shows value: %d', call_value)
        self.log.info('  Balance of session key: %d' % web3.eth.get_balance(sk))
        self.log.info('  Balance of account1:    %d' % web3.eth.get_balance(account.address))
        self.assertTrue(call_value == 2)
        self.assertTrue(balance_after1 < balance_before)

        # deactivate the session key and try to transact again (the network will not know about this nonce as it
        # wont reach it, so do not persist in this case
        self.deactivate_session_key(network.connection_url())
        nonce = network.get_next_nonce(self, web3, sk, persist_nonce=False)
        tx = network.build_transaction(self, web3, storage.contract.functions.store(3), nonce, sk, storage.GAS_LIMIT)
        try:
            web3.eth.send_transaction(tx)
            self.addOutcome(FAILED, outcomeReason='Do not expect exception to be thrown after deactivated')
        except Exception as e:
            self.log.error('Error sending raw transaction %s', e)
            self.addOutcome(PASSED, outcomeReason='Expect exception to be thrown after deactivated')

        # activate and transact again
        self.activate_session_key(network.connection_url())
        network.transact_unsigned(self, web3, storage.contract.functions.store(3), sk, storage.GAS_LIMIT)
        call_value = storage.contract.functions.retrieve().call()
        balance_after2 = web3.eth.get_balance(sk)
        self.log.info('  Call shows value: %d', call_value)
        self.log.info('  Balance of session key: %d' % balance_after2)
        self.log.info('  Balance of account1:    %d' % web3.eth.get_balance(account.address))
        self.assertTrue(call_value == 3)
        self.assertTrue(balance_after2 < balance_after1)

        # return the funds and deactivate
        tx = {'to': account.address, 'gasPrice': web3.eth.gas_price, 'chainId': web3.eth.chain_id}
        tx['gas'] = web3.eth.estimate_gas(tx)
        tx['value'] = balance_after2 - (tx['gas']*web3.eth.gas_price)
        self.log.info('  Expected gas cost: %d', tx['gas'])
        self.log.info('  Available balance: %d', balance_after2)
        self.log.info('  Value to transfer: %d', tx['value'])
        network.tx_unsigned(self, web3, tx, sk)
        balance_after3 = web3.eth.get_balance(sk)

        self.log.info('  Balance of session key: %d' % balance_after3)
        self.log.info('  Balance of account1:    %d' % web3.eth.get_balance(account.address))
        self.deactivate_session_key(network.connection_url())
        self.assertTrue(balance_after3 < balance_after2)

        # try and get the balance after deactivating
        balance_after4 = web3.eth.get_balance(sk)
        self.log.info('  Balance of session key after deactivating: %d' % balance_after4)
        self.assertTrue(balance_after4 == balance_after3)