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

        response = self.get_debug_event_log_relevancy(
            url=network.connection_url(),
            address=storage.address,
            signature=web3.keccak(text='Stored(uint256)').hex())
        self.log.info('Returned response: %s', response)

