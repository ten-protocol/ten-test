import os, shutil, re, base64, ast
from web3 import Web3
from eth_abi.abi import encode
from pysys.constants import PROJECT


class MerkleTreeHelper:
    """Helper used for value transfers from the L2 to the L1.

    When funds are transferred out of the L2 to the L1, the block containing the transaction has a crossChainTree field
    in the header, which contains a list of tuples, where each tuple has the hash of the value transfer event (v), and a
    hash of the cross chain message (m) received by the L1, e.g.

      [['v', '0xef10cef846b3934ebd733cf8d3fb330d3b2b4810621279cc5242a2b840570162'],
      ['m', '0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470']]

    All values in the tuples are used to create a merkle tree, where the root is also contained in the block header
    as the crossChainTreeHash field. For TEN users that perform a sendNative to transfer funds out of the L2, the block
    is accessible, as is the crossChainTree and crossChainTreeHash. This means they are able to take the hash of their
    value transfer, and the merkle tree root, and construct a proof that their value transfer is in that tree. They
    can use that proof on the L1 management contract for it to release their funds back to their L1 account.
    """

    @classmethod
    def create(cls, test):
        """Class method to create and return an instance of the proxy."""
        return MerkleTreeHelper(test)

    def __init__(self, test):
        """Instantiate an instance. """
        self.test = test

    def process_log_msg(self, log_msg):
        """Return the msg and hash of the log message published event, as stored in the cross chain tree. """
        abi_types = ['address', 'uint64', 'uint32', 'uint32', 'bytes', 'uint8']
        msg = [log_msg['sender'], log_msg['sequence'], log_msg['nonce'],
               log_msg['topic'], log_msg['payload'], log_msg['consistencyLevel']]
        msg_hash = Web3.keccak(encode(abi_types, msg)).hex()
        return msg, msg_hash

    def process_transfer(self, value_transfer):
        """Return the msg and hash of the value transfer event, as stored in the cross chain tree. """
        abi_types = ['address', 'address', 'uint256', 'uint64']
        msg = [value_transfer['sender'], value_transfer['receiver'], value_transfer['amount'], value_transfer['sequence']]
        msg_hash = Web3.keccak(encode(abi_types, msg)).hex()
        return msg, msg_hash

    def dump_tree(self, web3, tx_receipt, dump_file):
        """From a transaction receipt, extract block and the cross chain tree, decode it and dump to file.

        Dumping to file is so that the e2e test framework can pass construction of the tree and proof that a value
        transfer event exists in the key to an external javascript process. The proof needs to be constructed from the
        same open zepellin library used by the network, and hence cannot be performed in python. The method returns the
        block and decoded tree for reference should the caller require it.
        """
        block = web3.eth.get_block(tx_receipt.blockNumber)
        decoded = ast.literal_eval(base64.b64decode(block.crossChainTree).decode('utf-8'))
        with open(os.path.join(self.test.output, dump_file), 'w') as fp:
            for entry in decoded: fp.write('%s,%s\n' % (entry[0], entry[1]))
        return block, decoded

    def get_proof(self, dump_file, leaf_hash):
        """From a cross chain tree dump file, construct the merkle tree and obtain a proof of leaf entry.

        The method spawns a javascript process to read in the dump file containing the value transfer events and cross
        chain messages, to independently contstruct the tree, and then to obtain a proof of a leaf inclusion.
        """
        project = os.path.join(self.test.output, 'project')
        shutil.copytree(os.path.join(PROJECT.root,'src','javascript','projects','merkle_tree'), project)
        self.test.run_npm(args=['install', '--yes'], stdout='npm.out', stderr='npm.err', working_dir=project)
        stdout = os.path.join(self.test.output, 'merkle.out')
        stderr = os.path.join(self.test.output, 'merkle.err')
        script = os.path.join(project, 'src/merkle.mjs')
        args = ['--dump_file', os.path.join(self.test.output, dump_file)]
        args.extend(['--leaf_hash', leaf_hash])
        self.test.run_javascript(script, stdout, stderr, args)
        self.test.waitForGrep(os.path.join(self.test.output, 'merkle.out'), expr='Proof:')

        root = None
        proof = None
        regex1 = re.compile('Root: (?P<root>.*)$', re.M)
        regex2 = re.compile('Proof: (?P<proof>.*)$', re.M)
        with open(os.path.join(self.test.output, 'merkle.out'), 'r') as fp:
            for line in fp.readlines():
                result1 = regex1.search(line)
                result2 = regex2.search(line)
                if result1 is not None: root = result1.group('root')
                if result2 is not None: proof = result2.group('proof').split()
        return root, [] if proof=='undefined' else proof