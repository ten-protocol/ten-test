import base64, ast, os, shutil
from web3 import Web3
from eth_abi.abi import encode
from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        transfer_to = 1000000
        transfer_back = 4000000
        project = os.path.join(self.output, 'project')

        accnt = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')

        self.log.info('Send native from L1 to L2')
        tx_receipt, _, xchain_msg = accnt.l1.send_native(accnt.l2.account.address, transfer_to)
        accnt.l2.wait_for_message(xchain_msg)

        self.log.info('')
        self.log.info('Send native from L2 to L1')
        balance = accnt.l2.web3.eth.get_balance(accnt.l2.account.address)
        self.log.info('  balance:         %d', balance)

        # perform the transfer and log out the cross chain tree leafs (v=value transfer)
        tx_receipt, value_transfer, _ = accnt.l2.send_native(accnt.l1.account.address, transfer_back)
        block = accnt.l2.web3.eth.get_block(tx_receipt.blockNumber)
        decoded = ast.literal_eval(base64.b64decode(block.crossChainTree).decode('utf-8'))
        self.log.info('  value_transfer:   %s', list(value_transfer.values()))
        self.log.info('  cross_chain:      %s', decoded)
        self.log.info('  merkle_root:      %s', block.crossChainTreeHash)
        with open(os.path.join(self.output, 'cross_chain.log'), 'w') as fp:
            for entry in decoded: fp.write('%s,%s\n' % (entry[0], entry[1]))

        # construct the hash of the value transfer and compare with the xchain tree
        abi_types = ['address', 'address', 'uint256', 'uint64']
        values = [value_transfer['sender'], value_transfer['receiver'],
                  value_transfer['amount'], value_transfer['sequence']]
        encoded_data = encode(abi_types, values)
        hash_result = Web3.keccak(encoded_data).hex()
        self.assertTrue(hash_result == decoded[0][1])

        # pass the cross chain tree leafs to javascript so we can compute the tree and validate
        # we have the same based on the root hash
        shutil.copytree(self.input, project)
        self.run_npm(args=['install', '--yes'], stdout='npm.out', stderr='npm.err', working_dir=project)
        stdout = os.path.join(self.output, 'merkle.out')
        stderr = os.path.join(self.output, 'merkle.err')
        script = os.path.join(project, 'src/merkle.mjs')
        args = ['--input', os.path.join(self.output, 'cross_chain.log')]
        self.run_javascript(script, stdout, stderr, args)