import json, base64, os, rlp
from pysys.constants import FAILED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage
from eth_account._utils.legacy_transactions import serializable_unsigned_transaction_from_dict


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway and deploy the storage contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # get a session key for this connection and fund it
        self.log.info('')
        self.log.info('Create and fund a session key for all subsequent transactions')
        sk = self.get_session_key(network.connection_url())
        address = web3.to_checksum_address(sk)
        tx = {'to': address, 'value': web3.to_wei(0.01, 'ether'), 'gasPrice': web3.eth.gas_price, 'chainId': web3.eth.chain_id}
        tx['gas'] = web3.eth.estimate_gas(tx)
        network.tx(self, web3, tx, account)
        self.activate_session_key(network.connection_url())

        # transact using the session key, unsigned sent using web3
        self.log.info('')
        self.log.info('Transact using the session key, unsigned sent using web3')
        nonce = network.get_next_nonce(self, web3, address, persist_nonce=True)
        tx = network.build_transaction(self, web3, storage.contract.functions.store(2), nonce, address, storage.GAS_LIMIT)
        tx_hash = network.send_unsigned_transaction(self, web3, nonce, address, tx, persist_nonce=True)
        tx_recp = network.wait_for_transaction(self, web3, nonce, address, tx_hash, persist_nonce=True)
        if tx_recp.status != 1:
            network.replay_transaction(web3, tx, tx_recp)
            self.addOutcome(FAILED, abortOnError=True)
        self.assertTrue(storage.contract.functions.retrieve().call() == 2)

        # transact using session key, unsigned but using getStorageAt - bit involved but create the tx, build it,
        # serialise and slp encode it, then base64 encode it to be sent to the network
        self.log.info('')
        self.log.info('Transact using session key, unsigned but using getStorageAt')
        target = storage.contract.functions.store(5)
        tx = {'nonce': network.get_next_nonce(self, web3, address, True), 'chainId': web3.eth.chain_id,
              'gasPrice': web3.eth.gas_price}
        tx['gas'] = target.estimate_gas(tx)
        build_tx = target.build_transaction(tx)
        unsigned_tx = serializable_unsigned_transaction_from_dict(build_tx)
        b64_encoded_tx = base64.b64encode(rlp.encode(list(unsigned_tx))).decode()
        tx_hash = self.send_unsigned_against_session_key(network.connection_url(), b64_encoded_tx)
        tx_recp = network.wait_for_transaction(self, web3, nonce, address, tx_hash, persist_nonce=True)
        if tx_recp.status != 1:
            network.replay_transaction(web3, tx, tx_recp)
            self.addOutcome(FAILED, abortOnError=True)
        self.assertTrue(storage.contract.functions.retrieve().call() == 5)


        # deactivate the key
        self.deactivate_session_key(network.connection_url())
