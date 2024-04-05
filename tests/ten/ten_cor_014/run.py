import os
from pysys.constants import FAILED, PASSED
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):

    def execute(self):
        expected_keys = ['blockHash', 'blockNumber', 'contractAddress', 'cumulativeGasUsed', 'effectiveGasPrice',
                         'from', 'gasUsed', 'logs', 'logsBloom', 'status', 'to', 'transactionHash', 'transactionIndex',
                         'type']

        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # get the receipt sort the fields
        tx_receipt = network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS_LIMIT)
        keys = list(tx_receipt.keys())
        keys.sort()

        # log out the receipt entries
        with open(os.path.join(self.output, '%s.log' % self.mode), 'w') as fp:
            for key in keys:
                fp.write('%s: %s\n' % (key, tx_receipt[key]))

        # check the expected keys are seen in the list of fields
        passed = True
        for k in expected_keys:
            if k not in keys:
                passed = False
                self.addOutcome(FAILED, 'Key %s is missing' % k)
        if passed: self.addOutcome(PASSED, 'All expected keys seen')
