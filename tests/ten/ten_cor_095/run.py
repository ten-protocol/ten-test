import json, os
import base64, hashlib
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy a contract and get the debug event log relevancy on the Storage event
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        self.log.info('Storage contract address is %s', storage.address)

        # transact against the contract
        tx_receipt_1 = network.transact(self, web3, storage.contract.functions.store(0), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time))
        tx_receipt_2 = network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS_LIMIT)
        self.log.info('  tx_receipt_1.transactionHash:     %s' % tx_receipt_1.transactionHash.hex())
        self.log.info('  tx_receipt_1.blockNumber:         %s' % tx_receipt_1.blockNumber)
        self.log.info('  tx_receipt_2.transactionHash:     %s' % tx_receipt_2.transactionHash.hex())
        self.log.info('  tx_receipt_2.blockNumber:         %s' % tx_receipt_2.blockNumber)

        # call from first block to latest ... should have both events
        response_1 = self.get_debug_event_log_relevancy( url=network.connection_url(),
            address=storage.address, signature=web3.keccak(text='Stored(uint256)').hex(),
            fromBlock=hex(tx_receipt_1.blockNumber), toBlock='latest')

        # dump for reference
        self.dump(response_1[0], 'response_1_event_1.log')
        self.dump(response_1[1], 'response_1_event_2.log')

        # contract has no explicit configuration so should be default
        self.assertTrue(len(response_1) == 2)
        self.assertTrue(response_1[0]['transactionHash'] == tx_receipt_1.transactionHash.hex())
        self.assertTrue(response_1[1]['transactionHash'] == tx_receipt_2.transactionHash.hex())
        self.assertTrue(response_1[0]['defaultContract'] == True)
        self.assertTrue(response_1[1]['defaultContract'] == True)

    def dump(self, obj, filename):
        with open(os.path.join(self.output, filename), 'w') as file:
            json.dump(obj, file, indent=4)