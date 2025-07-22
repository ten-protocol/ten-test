from pysys.constants import FAILED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect players to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # user deploys contract and performs some transactions against it
        self.log.info('')
        self.log.info('User deploys contract and submits transactions against it')
        storage = Storage(self, web3, 0)
        storage.deploy(network, account)

        tx_receipt = network.transact(self, web3, storage.contract.functions.store(78), account, storage.GAS_LIMIT)
        tx_block_hash = tx_receipt['blockHash'].hex()
        self.log.info('Transaction made with reported block hash as %s', tx_block_hash)

        # check to ensure the total is the total blocks in the network, not the total in the return set
        self.log.info('')
        self.log.info('Doing a couple of calls on different pages sizes')
        r1 = self.scan_get_block_listing(offset=0, size=10)
        r2 = self.scan_get_block_listing(offset=0, size=20)
        self.assertTrue(r1['Total'] != 10 and r2['Total'] != 20,
                        assertMessage='The total return should be the total in the network, not the page size')

        # check to get all the blocks
        self.wait(1.1*float(self.block_time))
        self.log.info('')
        self.log.info('Calling to iterate through all the blocks')
        offset = 0
        total = 0
        found_block = False
        while True:
            self.log.info('  Calling for offset %d, total so far %d' % (offset, total))
            r = self.scan_get_block_listing(offset=offset, size=10)

            for block in r['BlocksData']:
                #self.log.info('    Block number %d', int(block['blockHeader']['number'], 16))
                if block['blockHeader']['hash'] == tx_block_hash:
                    self.log.info('    Block found in offset call %d', offset)
                    found_block = True

            if len(r['BlocksData']) < 10:
                total += len(r['BlocksData'])
                reported_total = r['Total']
                break
            offset += 10
            total += 10
        self.log.info('Total blocks read were %d, reported last total was %d' % (total, reported_total))
        self.assertTrue(total == reported_total, assertMessage='Total read should match total reported')
        self.assertTrue(found_block, assertMessage='We should see the block in the returned set for our tx')

        # check to see if we can read a large page
        self.log.info('')
        self.log.info('Doing a call on a large page size')
        try:
            self.scan_get_block_listing(offset=5, size=50)
        except Exception as e:
            self.log.warn('Exception thrown: %s', e)
            self.addOutcome(FAILED, outcomeReason='We should not throw an exception on parse error')