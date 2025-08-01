import os, json
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import TransparentGuessGame


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # user deploys the contract and performs some transactions against it
        game = TransparentGuessGame(self, web3)
        game.deploy(network, account)
        tx_receipt = network.transact(self, web3, game.contract.functions.guess(8), account, game.GAS_LIMIT)
        tx_hash = tx_receipt['transactionHash'].hex()
        tx_block_hash = tx_receipt['blockHash'].hex()

        # get the transaction by hash
        _ = self.query(tx_hash, 'tx_hash')

        # get the block by hash
        response = self.query(tx_block_hash, 'tx_block_hash')

        # get the block by height
        tx_block_height = response['ResultsData'][0]['height']
        _ = self.query(tx_block_height, 'tx_block_height')

        # get the block by sequence
        tx_block_seq = response['ResultsData'][0]['sequence']
        _ = self.query(tx_block_seq, 'tx_block_seq')

    def query(self, query, name):
        self.log.info('')
        self.log.info('Running query for %s, param %s', name, query)
        response = self.scan_search(query)
        with open(os.path.join(self.output, '%s.json'%name), 'w') as f: json.dump(response, f, indent=4)
        return response
