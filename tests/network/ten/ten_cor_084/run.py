from pysys.constants import FAILED
from web3._utils.events import EventLogErrorFlags
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.relevancy import FieldSenderRelevancy


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect the accounts to the network
        network_1 = self.get_network_connection()
        network_2 = self.get_network_connection()
        network_3 = self.get_network_connection()
        web3_1, account_1 = network_1.connect_account1(self)
        web3_2, account_2 = network_2.connect_account2(self)
        web3_3, account_3 = network_3.connect_account3(self)

        # account 3 deploys and interacts with the contract
        relevancy_3 = FieldSenderRelevancy(self, web3_3)
        relevancy_3.deploy(network_3, account_3)
        relevancy_2 = FieldSenderRelevancy.clone(web3_2, account_2, relevancy_3)
        relevancy_1 = FieldSenderRelevancy.clone(web3_3, account_2, relevancy_3)

        target = relevancy_1.contract.functions.twoIndexedAddresses
        tx_rcpt = network_3.transact(self, web3_3, target(account_1.address, account_2.address), account_3,
                                     relevancy_1.GAS_LIMIT)

        # all accounts should be able to retrieve the tx receipt and see the events
        try:
            receipt = web3_1.eth.get_transaction_receipt(tx_rcpt.transactionHash)
            logs = relevancy_1.contract.events.TwoIndexedAddresses().process_receipt(receipt, EventLogErrorFlags.Discard)
            self.assertTrue(logs[0]['args']['addr1'] == account_1.address, assertMessage='Logs should show the addr1')
        except:
            self.addOutcome(FAILED, 'Unable to get logs for account 1')

        try:
            receipt = web3_2.eth.get_transaction_receipt(tx_rcpt.transactionHash)
            logs = relevancy_2.contract.events.TwoIndexedAddresses().process_receipt(receipt, EventLogErrorFlags.Discard)
            self.assertTrue(logs[0]['args']['addr1'] == account_1.address, assertMessage='Logs should show the addr1')
        except:
            self.addOutcome(FAILED, 'Unable to get logs for account 1')

        try:
            receipt = web3_3.eth.get_transaction_receipt(tx_rcpt.transactionHash)
            logs = relevancy_3.contract.events.TwoIndexedAddresses().process_receipt(receipt, EventLogErrorFlags.Discard)
            self.assertTrue(logs[0]['args']['addr1'] == account_1.address, assertMessage='Logs should show the addr1')
        except:
            self.addOutcome(FAILED, 'Unable to get logs for account 1')
