import base64, ast, os, shutil, re
from web3 import Web3
from eth_abi.abi import encode
from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        transfer = 4000000000000000

        # create the bridge user
        accnt = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')
        l1_before = accnt.l1.web3.eth.get_balance(accnt.l1.account.address)
        l2_before = accnt.l2.web3.eth.get_balance(accnt.l2.account.address)
        self.log.info('  l1_balance:   %s', l1_before)
        self.log.info('  l2_balance:   %s', l2_before)

        # send funds from the L2 to the L1
        self.log.info('Send native from L2 to L1')
        tx_receipt, value_transfer, _ = accnt.l2.send_native(accnt.l1.account.address, transfer)
        l2_cost = int(tx_receipt.gasUsed) * accnt.l2.web3.eth.gas_price
