import base64, ast
from web3 import Web3
from eth_abi.abi import encode
from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties
from ten.test.utils.merkle import MerkleTree


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        transfer_to = 1000000
        transfer_back = 4000000

        accnt = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')

        self.log.info('Send native from L1 to L2')
        tx_receipt, _, xchain_msg = accnt.l1.send_native(accnt.l2.account.address, transfer_to)
        accnt.l2.wait_for_message(xchain_msg)

        for i in range(0,3):
            self.log.info('')
            self.log.info('Send native from L2 to L1')
            balance = accnt.l2.web3.eth.get_balance(accnt.l2.account.address)
            self.log.info('  balance:         %d', balance)

            # perform the transfer
            tx_receipt, value_transfer, _ = accnt.l2.send_native(accnt.l1.account.address, transfer_back)
            block = accnt.l2.web3.eth.get_block(tx_receipt.blockNumber)
            decoded = ast.literal_eval(base64.b64decode(block.crossChainTree).decode('utf-8'))
            self.log.info('  value_transfer:   %s', list(value_transfer.values()))
            self.log.info('  cross_chain:      %s', decoded)

            # construct the hash of the value transfer and compare with the xchain tree
            abi_types = ['address', 'address', 'uint256', 'uint64']
            values = [value_transfer['sender'], value_transfer['receiver'],
                      value_transfer['amount'], value_transfer['sequence']]
            encoded_data = encode(abi_types, values)
            hash_result = Web3.keccak(encoded_data).hex()
            self.assertTrue(hash_result == decoded[0][1])

            merkle_tree = MerkleTree(["v"+x[1] for x  in decoded])
            root = merkle_tree.getRootHash()
            self.log.info('  merkle_root:      %s', root)
            # assert the root is correct here once added into the block header
