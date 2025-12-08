from eth_utils import keccak
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect players to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # user deploys contract and performs a transactions against it
        self.log.info('')
        self.log.info('User deploys contract and submits transactions against it')
        storage = Storage(self, web3, 0)
        storage.deploy(network, account)

        tx_receipt = network.transact(self, web3, storage.contract.functions.store(78), account, storage.GAS_LIMIT)
        tx_hash = tx_receipt['transactionHash'].hex()
        tx_block_number = tx_receipt['blockNumber']
        self.log.info('Transaction made with reported hash as %s', tx_hash)

        # get the transaction by its hash and validate
        tx = self.scan_get_transaction(hash=tx_hash)
        self.assertTrue(tx['TransactionHash'] == tx_hash, assertMessage='Transaction hashes should match')
        self.assertTrue(tx['BatchHeight'] == tx_block_number, assertMessage='Batch numbers should match')

        # you don't have to be mad to work here, but ...
        error = self.scan_get_transaction(hash='0x'+keccak(b'Wibble').hex(), return_error=True)
        self.assertTrue(error == 'not found', assertMessage='Wibble should not be found')
