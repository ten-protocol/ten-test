import time
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage
from ten.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract make some transactions
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # do a transaction and wait for the block number to increase
        tx = network.transact(self, web3, storage.contract.functions.store(0), account, storage.GAS_LIMIT)
        block_number = web3.eth.get_block_number()
        start = time.time()
        while block_number <= tx.blockNumber:
            if time.time() - start > (3*float(self.block_time)): raise TimeoutError('Timed out waiting for block number to increase')
            self.log.info('Waiting for the block number to increase (last %d, current %d)' %(tx.blockNumber, block_number))
            time.sleep(float(self.block_time))
            block_number = web3.eth.get_block_number()

        # do some more transactions and then kick off the event subscriber
        tx = network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT)

        # run the javascript event log subscriber in the background
        subscriber = FilterLogSubscriber(self, network)
        subscriber.run(
            decode_as_stored_event=True,
            filter_from_block=tx.blockNumber,
            filter_topics=[web3.keccak(text='Stored(uint256)').hex()]
        )
        subscriber.subscribe()

        # perform some more transactions
        network.transact(self, web3, storage.contract.functions.store(3), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(4), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(5), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 2)

        # wait and validate
        self.waitForGrep(file=subscriber.stdout, expr='Stored value = 5', timeout=20)
        self.assertOrderedGrep(file=subscriber.stdout, exprList=['Stored value = %d' % x for x in range(1, 6)])
