import secrets, random, os, shutil
from web3 import Web3
from datetime import datetime
from collections import OrderedDict
from obscuro.test.contracts.error import Error
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.gnuplot import GnuplotHelper


class PySysTest(ObscuroNetworkTest):
    ITERATIONS = 5000

    def execute(self):
        self.execute_run()

    def execute_run(self):
        # connect to the network
        network = self.get_network_connection()
        web3_deploy, account_deploy = network.connect_account1(self)

        # we need to perform a transaction on the account to ensure the nonce is greater than zero for the
        # following bulk loading (a hack to avoid count=0 being considered a new deployment and clearing the db)
        error = Error(self, web3_deploy)
        error.deploy(network, account_deploy)

        # use an ephemeral accounts so we don't need to manage nonce through persistence
        web3, account = network.connect(self, private_key=secrets.token_hex())
        accounts = [Web3().eth.account.privateKeyToAccount(x).address for x in [secrets.token_hex()]*25]

        # bulk load transactions to the accounts, and wait for the last
        self.log.info('Creating and signing %d transactions', self.ITERATIONS)
        value = web3.toWei(0.0000000001, 'ether')
        gas_price = web3.eth.gas_price
        chain_id = network.chain_id()

        txs = []
        for i in range(0, self.ITERATIONS):
            tx = self.create_signed_tx(network, account, i, random.choice(accounts), value, gas_price, chain_id)
            txs.append((tx, i))

        self.log.info('Bulk sending transactions to the network')
        receipts = []
        for tx in txs:
            receipts.append((network.send_transaction(self, web3, tx[1], account, tx[0], False), tx[1]))

        self.log.info('Waiting for last transaction')
        network.wait_for_transaction(self, web3, receipts[-1][1], account, receipts[-1][0], False, timeout=600)

        # bin the data into timestamp intervals and log out to file
        self.log.info('Constructing binned data from the transaction receipts')
        bins = OrderedDict()
        for receipt in receipts:
            block_number_deploy = web3.eth.get_transaction(receipt[0]).blockNumber
            timestamp = int(web3.eth.get_block(block_number_deploy).timestamp)
            bins[timestamp] = 1 if timestamp not in bins else bins[timestamp] + 1

        times = list(bins)
        first = times[0]
        with open(os.path.join(self.output, 'data.bin'), 'w') as fp:
            for i in range(times[0], times[-1]+1):
                num = bins[i] if i in bins else 0
                fp.write('%d %d\n' % ((i - first), num))

        # graph the output
        branch = GnuplotHelper.buildInfo().branch
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        duration = times[-1]-times[0]
        average = float(self.ITERATIONS) / float(duration) if duration != 0 else 0
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'), branch, date,
                            str(self.mode), str(self.ITERATIONS), str(duration), '%.3f'%average)

    def create_signed_tx(self, network, account, nonce, address, value, gas_price, chain_id):
        """Creates a signed transaction ready for the sending of funds to an account. """
        tx = {'nonce': nonce,
              'to': address,
              'value': value,
              'gas': 4 * 720000,
              'gasPrice': gas_price,
              'chainId': chain_id
              }
        return network.sign_transaction(self, tx, nonce, account, False)

    def execute_graph(self):
        """Test method to develop graph creation. """
        branch = GnuplotHelper.buildInfo().branch
        duration = 114
        average = 43.860
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        shutil.copy(os.path.join(self.input, 'data.bin'), os.path.join(self.output, 'data.bin'))
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'),
                            branch, date,
                            str(self.mode), str(self.ITERATIONS), str(duration), '%.3f'%average)