import base64
from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        transfer_to = 1000000
        transfer_back = 1000000

        accnt1 = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')

        l1_balance = accnt1.l1.web3.eth.get_balance(accnt1.l1.account.address)
        l2_balance = accnt1.l2.web3.eth.get_balance(accnt1.l2.account.address)
        self.log.info('Account balances;')
        self.log.info('   L1 before: %d', l1_balance)
        self.log.info('   L2 before: %d', l2_balance)

        self.log.info('Send native from L1 to L2')
        tx_receipt, _, xchain_msg = accnt1.l1.send_native(accnt1.l2.account.address, transfer_to)
        accnt1.l2.wait_for_message(xchain_msg)

        l1_balance1 = accnt1.l1.web3.eth.get_balance(accnt1.l1.account.address)
        l2_balance1 = accnt1.l2.web3.eth.get_balance(accnt1.l2.account.address)
        self.log.info('Account balances;')
        self.log.info('   L1 after:  %d', l1_balance1)
        self.log.info('   L2 after:  %d', l2_balance1)
        self.log.info('   L1 decr:   %d', (l1_balance-l1_balance1))
        self.log.info('   L2 incr:   %d', (l2_balance1-l2_balance))

        self.log.info('Send native from L2 to L1')
        tx_receipt, value_transfer, xchain_msg = accnt1.l2.send_native(accnt1.l1.account.address, transfer_back)

        l1_balance2 = accnt1.l1.web3.eth.get_balance(accnt1.l1.account.address)
        l2_balance2 = accnt1.l2.web3.eth.get_balance(accnt1.l2.account.address)
        self.log.info('Account balances;')
        self.log.info('   L1 after:  %d', l1_balance2)
        self.log.info('   L2 after:  %d', l2_balance2)
        self.log.info('   L1 incr:   %d', (l1_balance2-l1_balance1))
        self.log.info('   L2 decr:   %d', (l2_balance1-l2_balance2))

        block = accnt1.l2.web3.eth.get_block(tx_receipt.blockNumber)
        self.log.info('value_transfer:   %s', value_transfer)
        self.log.info('cross_chain_tree: %s', block.crossChainTree)
        self.log.info(base64.b64decode(block.crossChainTree))
        self.log.info(base64.b64encode('valueTransfer'.encode("ascii")))
        base64.b64decode('woidjw==').hex()
        # encode the event values, kecca256 it should point to a hash in the cross chain tree
        # which will be the one you build a proof for
