import secrets, os
from datetime import datetime
from collections import OrderedDict
from web3.exceptions import TimeExhausted
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):
    ITERATIONS = 1024      # don't exceed bulk loading more than 1024 (single client used)

    def execute(self):
        # use an ephemeral account so we don't need to manage nonce through persistence
        self.log.info('')
        self.log.info('Creating ephemeral account to distribute funds from')
        network = self.get_network_connection()
        web3_send, account_send = network.connect(self, private_key=secrets.token_hex(), check_funds=False)
        self.distribute_native(account_send, amount=0.001)

        # connect a bunch of recipient clients to receive funds
        self.log.info('')
        self.log.info('Creating ephemeral account to receive funds')
        web3_receive, account_receive = network.connect(self, private_key=secrets.token_hex(), check_funds=False)

        # bulk load transactions to the accounts, and wait for the last
        self.log.info('')
        self.log.info('Creating and signing %d transactions', self.ITERATIONS)
        value = web3_send.to_wei(0.0000000001, 'ether')
        gas_price = web3_send.eth.gas_price
        chain_id = network.chain_id()

        txs = []
        for nonce in range(0, self.ITERATIONS):
            tx = self.create_signed_tx(network, account_send, nonce, account_receive.address, value, gas_price, chain_id)
            txs.append((tx, nonce))

        self.log.info('Bulk sending transactions to the network')
        balance_before = web3_send.from_wei(web3_send.eth.get_balance(account_send.address), 'gwei')
        tx_hashes = []
        for tx in txs:
            tx_hashes.append((network.send_transaction(self, web3_send, tx[1], account_send, tx[0], False, verbose=False), tx[1]))
        balance_after_send = web3_send.from_wei(web3_send.eth.get_balance(account_send.address), 'gwei')

        try:
            self.log.info('Waiting for last transaction')
            web3_send.eth.wait_for_transaction_receipt(tx_hashes[-1][0], timeout=30)

        except TimeExhausted as e:
            count = 0
            for tx_hash, nonce in tx_hashes:
                try: web3_send.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
                except Exception as e:
                    self.log.info('Transaction %d failed', count)
                    break
                count = count + 1

        # print out balances for information
        self.log.info('')
        self.log.info('Printing out balance information')
        balance_after_wait = web3_send.from_wei(web3_send.eth.get_balance(account_send.address), 'gwei')
        self.log.info('Sender balance before send: %d gwei', balance_before)
        self.log.info('Sender balance after send:  %d gwei', balance_after_send)
        self.log.info('Sender balance after wait: %d gwei', balance_after_wait)
        balance_receiver = web3_receive.from_wei(web3_send.eth.get_balance(account_receive.address), 'gwei')
        self.log.info('Receiver balance after wait: %d gwei', balance_receiver)

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
