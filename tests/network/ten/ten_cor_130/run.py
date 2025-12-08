import math
from collections import Counter
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.system import TenSystemCallsCaller


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()

        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        caller = TenSystemCallsCaller(self, web3)
        caller.deploy(network, account)

        # send in the transactions
        results = caller.contract.functions.callRandomNumbers(props.L2TenSystemCalls, 1000).call()
        entropy = self.entropy_bucketed(results)
        self.log.info('Entropy of the returned sequence is %.2f' % entropy)
        self.log.info('Length of returned list is %d' % len(results))
        self.log.info('Length of returned set is %d' % len(set(results)))
        self.assertTrue(entropy > 7.5 and entropy < 8, assertMessage='Entropy should be nearly 8')
        self.assertTrue(len(results) == len(set(results)), assertMessage='There should be no duplicates')

    def entropy_bucketed(self, data, bucket_bits=8):
        buckets = [(x >> (256 - bucket_bits)) for x in data]
        count = Counter(buckets)
        total = len(buckets)
        return -sum((freq / total) * math.log2(freq / total) for freq in count.values())
