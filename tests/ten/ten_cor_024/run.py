import base64
from web3 import Web3
from eth_abi.abi import encode
from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        transfer_to = 1000000
        transfer_back = 500000

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
        tx_receipt, value_transfer, _ = accnt1.l2.send_native(accnt1.l1.account.address, transfer_back)
        block1 = accnt1.l2.web3.eth.get_block(tx_receipt.blockNumber)
        decoded = base64.b64decode(block1.crossChainTree)
        self.log.info('value_transfer:   %s', value_transfer)
        self.log.info('cross_chain:      %s', decoded)
        self.log.info('cross_chain:      %s', decoded.decode('utf-8'))

        self.log.info('Constructing hash of the value transfer event')
        abi_types = ['address', 'address', 'uint256', 'uint64']
        values = [value_transfer['sender'], value_transfer['receiver'],
                  value_transfer['amount'], value_transfer['sequence']]
        encoded_data = encode(abi_types, values)
        hash_result = Web3.keccak(encoded_data).hex()
        self.log.info('hash_result:      %s', hash_result)
