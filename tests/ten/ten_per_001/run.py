import os, time
from datetime import datetime
from collections import OrderedDict
from web3.exceptions import TimeExhausted
from pysys.constants import FAILED, PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):
    ITERATIONS = 5000       # number of iterations per client

    def __init__(self, descriptor, outsubdir, runner):
        super().__init__(descriptor, outsubdir, runner)
        self.gas_price = 0
        self.gas_limit = 0
        self.chain_id = 0
        self.value = 100

    def execute(self):
        # connect to the network on the primary connection
        network = self.get_network_connection(name='local' if self.is_local_ten() else 'primary', verbose=False)
        web3, _ = network.connect_account1(self)

        # use an ephemeral account, so we don't need to manage nonce through persistence
        self.log.info('')
        self.log.info('Creating ephemeral account to distribute funds from')
        web3_send, account_send = network.connect(self, private_key=self.get_ephemeral_pk(), check_funds=False)

        # use an ephemeral account to receive funds
        self.log.info('')
        self.log.info('Creating ephemeral account to receive funds')
        web3_recv, account_recv = network.connect(self, private_key=self.get_ephemeral_pk(), check_funds=False)

        # determine constants and funds required to run the test
        self.log.info('')
        self.log.info('Determine constants and funds required to run the test')
        self.chain_id = network.chain_id()
        self.gas_price = web3_send.eth.gas_price
        self.gas_limit = web3.eth.estimate_gas({'to': account_recv.address, 'value': self.value, 'gasPrice': self.gas_price})
        funds_needed = 1.1 * self.ITERATIONS * (self.gas_price*self.gas_limit + self.value)
        self.log.info('Gas price:    %d', self.gas_price)
        self.log.info('Gas estimate: %d', self.gas_limit)
        self.log.info('Funds needed: %d', funds_needed)
        self.distribute_native(account_send, amount=web3_send.from_wei(funds_needed, 'ether'))

        # bulk load transactions, and wait for the last
        self.log.info('')
        self.log.info('Creating and signing %d transactions', self.ITERATIONS)
        txs = []
        for nonce in range(0, self.ITERATIONS):
            txs.append((self.create_signed_tx(network, account_send, nonce, account_recv.address), nonce))

        self.log.info('Bulk sending transactions to the network')
        balance_before = web3_send.eth.get_balance(account_send.address)
        tx_hashes = []
        for tx in txs:
            tx_hashes.append((network.send_transaction(self, web3_send, tx[1], account_send, tx[0], False, verbose=False), tx[1]))
        balance_after_send = web3_send.eth.get_balance(account_send.address)

        self.log.info('Waiting for last transaction to be mined')
        try:
            web3_send.eth.wait_for_transaction_receipt(tx_hashes[-1][0], timeout=30)
        except TimeExhausted as e:
            count = 0
            for tx_hash, nonce in tx_hashes:
                try: web3_send.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
                except Exception as e:
                    self.log.info('Transaction %d failed', count)
                    self.addOutcome(FAILED)
                count = count + 1
        balance_after_wait = web3_send.eth.get_balance(account_send.address)
        balance_receiver = web3_send.eth.get_balance(account_recv.address)

        # print out balances for information
        self.log.info('')
        self.log.info('Printing out balance information')
        self.log.info('Sender balance before send:  %d wei', balance_before)
        self.log.info('Sender balance after send:   %d wei', balance_after_send)
        self.log.info('Sender balance after wait:   %d wei', balance_after_wait)
        self.log.info('Sender balance delta:        %d wei', (balance_before - balance_after_wait))
        self.log.info('Receiver balance after wait: %d wei', balance_receiver)

        # bin the data into timestamp intervals and log out to file
        self.log.info('')
        self.log.info('Constructing binned data from the transaction receipts and graphing')
        bins = OrderedDict()
        for tx_hash, nonce in tx_hashes:
            block_number_deploy = web3_send.eth.get_transaction(tx_hash).blockNumber
            timestamp = int(web3_send.eth.get_block(block_number_deploy).timestamp)
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

        # persist the result
        self.results_db.insert_result(self.descriptor.id, self.mode, int(time.time()), average)

        # passed if no failures (though pdf output should be reviewed manually)
        self.addOutcome(PASSED)

    def create_signed_tx(self, network, account, nonce, address):
        """Creates a signed transaction ready for the sending of funds to an account. """
        tx = {'nonce': nonce,
              'to': address,
              'value': self.value,
              'gas': self.gas_limit,
              'gasPrice': self.gas_price,
              'chainId': self.chain_id
              }
        return network.sign_transaction(self, tx, nonce, account, persist_nonce=False)
