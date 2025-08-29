import re
from pysys.constants import FAILED
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
        self.log.info('')
        self.log.info('Create, activate and transact using a session key')
        sk = self.get_session_key(network.connection_url())
        tx = {'to': sk, 'value': web3.to_wei(0.01, 'ether'), 'gasPrice': web3.eth.gas_price,
              'chainId': web3.eth.chain_id}
        tx['gas'] = web3.eth.estimate_gas(tx)
        network.tx(self, web3, tx, account)

        # transact using the session key
        network.transact_unsigned(self, web3, storage.contract.functions.store(22), sk, storage.GAS_LIMIT)
        self.assertTrue(storage.contract.functions.retrieve().call() == 22)

        # delete the session key
        self.log.info('')
        self.log.info('Delete the session key')
        self.delete_session_key(network.connection_url())

        # transact using the deleted session key
        self.log.info('')
        self.log.info('Try to transact through a deleted session key')
        try:
            network.transact_unsigned(self, web3, storage.contract.functions.store(2), sk, storage.GAS_LIMIT)
            self.addOutcome(FAILED, outcomeReason='Exception should be raised')
        except Exception as e:
            self.log.info('Exception type: %s', type(e).__name__)
            self.log.info('Exception args: %s', e.args)
            regex = re.compile('illegal access', re.M)
            self.assertTrue(regex.search(e.args[0]['message']) is not None)
