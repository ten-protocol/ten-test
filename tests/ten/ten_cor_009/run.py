from ten.test.basetest import TenNetworkTest
from ten.test.contracts.relevancy import Relevancy
from ten.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy a contract that emits a non-lifecycle event on calling a specific method as a transaction
        relevancy = Relevancy(self, web3)
        relevancy.deploy(network, account)
        self.log.info('Relevancy contract address is %s', relevancy.address)

        # run the javascript event log subscriber in the background
        subscriber = FilterLogSubscriber(self, network)
        subscriber.run(decode_as_stored_event=False)
        subscriber.subscribe()

        # perform some transactions
        tx_recp = network.transact(self, web3, relevancy.contract.functions.indexedAddressAndNumber(account.address),
                                   account, relevancy.GAS_LIMIT)
        self.log.info('First transaction block hash %s', tx_recp.blockHash.hex())
        self.log.info('First transaction tx hash %s', tx_recp.transactionHash.hex())
        response = self.get_debug_event_log_relevancy(tx_recp.transactionHash.hex())

        self.waitForSignal(file='subscriber.out', expr='Full log:', condition='==1', timeout=10)
        self.assertLineCount(file='subscriber.out', expr='Full log:', condition='==1')

        self.assertTrue(response[0]['address'] == relevancy.address)
        self.assertTrue(response[0]['topics'][0] == web3.keccak(text='IndexedAddressAndNumber(address,uint256)').hex())
        self.assertTrue(response[0]['transactionHash'] == tx_recp.transactionHash.hex())
        self.assertTrue(response[0]['blockHash'] == tx_recp.blockHash.hex())
        self.assertTrue(response[0]['logIndex'] == 0)
        self.assertTrue(response[0]['blockNumber'] == tx_recp.blockNumber)
        self.assertTrue(response[0]['lifecycleEvent'] == False)
