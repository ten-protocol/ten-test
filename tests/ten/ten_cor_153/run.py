from collections import Counter
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
        r1 = self.scan_get_batch_listing(offset=0, size=10)
        r2 = self.scan_get_batch_listing(offset=0, size=20)
        self.assertTrue(r1['Total'] != 10 and r2['Total'] != 20,
                        assertMessage='The total return should be the total in the network, not the page size')

        # check to get all the blocks
        self.log.info('')
        self.log.info('Calling to iterate through all the batches')
        offset = 0
        total = 0
        reported_total = 0
        found_block = False
        numbers = []
        while True:
            self.log.info('  Calling for offset %d, total so far %d' % (offset, total))
            r = self.scan_get_batch_listing(offset=offset, size=10)

            try: # possible there are no more data and last page of 10 completed all
                for block in r['BatchesData']:
                    numbers.append(int(block['header']['number'], 16))
                    if block['header']['hash'] == tx_block_hash:
                        self.log.info('    Block found in offset call %d', offset)
                        found_block = True
            except:
                break

            if len(r['BatchesData']) < 10:
                total += len(r['BatchesData'])
                reported_total = r['Total']
                break
            offset += 10
            total += 10

        self.log.info('Total blocks read were %d, reported last total was %d' % (total, reported_total))
        self.assertTrue(total == reported_total, assertMessage='Total read should match total reported')
        self.assertTrue(found_block, assertMessage='We should see the block in the returned set for our tx')
        self.assertTrue(self.differs_by_one(numbers), assertMessage='Batch numbers should differ by 1')

        duplicates = self.get_duplicates(numbers)
        if len(duplicates) > 0:
            self.log.info('Duplicates seen %s', duplicates)
            self.addOutcome(FAILED, 'There should be no duplicate batch numbers in the iterated set')

        # check to see if we can read a large page
        if reported_total > 50:
            self.log.info('')
            try:
                self.scan_get_batch_listing(offset=0, size=50)
                self.log.info('Doing a call on a large page size passed')
            except Exception as e:
                self.log.warn('Doing a call on a large page size failed')
                self.log.warn('Exception thrown: %s', e)
                self.addOutcome(FAILED, outcomeReason='We should not throw an exception on parse error')

    def differs_by_one(self, lst):
        result = True
        s = lst[0]
        for i in lst[1:]:
            if abs(s-i) != 1:
                self.log.warn('Previous batch number was %d and current is %d' % (s,i))
                result = False
            s = i
        return result

    def get_duplicates(self, lst):
        counts = Counter(lst)
        return [num for num, count in counts.items() if count > 1]