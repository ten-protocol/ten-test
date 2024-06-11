import base64, ast, os, shutil, re
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

        accnt = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')

        # send funds from the L1 to the L2
        self.log.info('Send native from L1 to L2')
        tx_receipt, _, xchain_msg = accnt.l1.send_native(accnt.l2.account.address, transfer_to)
        accnt.l2.wait_for_message(xchain_msg)

        # send funds from the L2 to the L1
        self.log.info('Send native from L2 to L1')
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

        root, proof = self.parse_merkle_output('cross_chain.log', hash_result)
        self.log.info('  calculated root:      %s', root)
        self.log.info('  calculated proof:     %s', proof)

        accnt.l1.release_funds(values, [proof], root)

    def parse_merkle_output(self, dump_file, hash_result):
        """Get the root and proof of a leaf entry in a tree dump to file. """
        project = os.path.join(self.output, 'project')
        shutil.copytree(self.input, project)
        self.run_npm(args=['install', '--yes'], stdout='npm.out', stderr='npm.err', working_dir=project)
        stdout = os.path.join(self.output, 'merkle.out')
        stderr = os.path.join(self.output, 'merkle.err')
        script = os.path.join(project, 'src/merkle.mjs')
        args = ['--input', os.path.join(self.output, dump_file)]
        args.extend(['--proof', 'v,%s' % hash_result])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(os.path.join(self.output, 'merkle.out'), expr='Proof:')

        root = None
        proof = None
        regex1 = re.compile('Root: (?P<root>.*)$', re.M)
        regex2 = re.compile('Proof: (?P<proof>.*)$', re.M)
        with open(os.path.join(self.output, 'merkle.out'), 'r') as fp:
            for line in fp.readlines():
                result1 = regex1.search(line)
                result2 = regex2.search(line)
                if result1 is not None: root = result1.group('root')
                if result2 is not None: proof = result2.group('proof')
        return root, proof
