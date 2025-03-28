from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        transfer = 1000

        network = self.get_network_connection()
        web3_1, acnt_1 = network.connect_account1(self)
        web3_2, acnt_2 = network.connect_account2(self)

        balance_1_before = web3_1.eth.get_balance(acnt_1.address)
        balance_2_before = web3_2.eth.get_balance(acnt_2.address)
        self.log.info('Account 1 balance before:  %d' % balance_1_before)
        self.log.info('Account 2 balance before:  %d' % balance_2_before)

        # a native funds transfer
        self.log.info('Perform a native funds transfer')
        tx = {'to': acnt_2.address, 'value': transfer, 'gasPrice': web3_1.eth.gas_price, 'chainId': web3_1.eth.chain_id}
        gas_price = web3_1.eth.gas_price
        estimate = web3_1.eth.estimate_gas(tx)
        tx['gas'] = int(estimate)

        self.log.info('Transaction gas estimate:  %d' % estimate)
        self.log.info('Gas being given         :  %d' % tx['gas'])
        receipt = network.tx(self, web3_1, tx, acnt_1, txstr='value transfer')
        if 'effectiveGasPrice' in receipt.keys(): gas_price = receipt.effectiveGasPrice
        self.log.info('Transaction gasUsed:       %d' % receipt.gasUsed)
        self.log.info('Transaction gasPrice:      %d' % gas_price)
        network.dump(receipt, 'receipt.log')

        balance_1_after = web3_1.eth.get_balance(acnt_1.address)
        balance_2_after = web3_2.eth.get_balance(acnt_2.address)
        self.log.info('')
        self.log.info('Account 1 balance after:   %d' % balance_1_after)
        self.log.info('Account 1 balance change:  %d' % (balance_1_before - balance_1_after))
        self.log.info('Account 1 expected change: %d' % ((receipt.gasUsed * gas_price) + transfer))
        self.log.info('')
        self.log.info('Account 2 balance after:   %d' % balance_2_after)
        self.log.info('Account 2 balance change:  %d' % (balance_2_after - balance_2_before))
        self.log.info('Account 2 expected change: %d' % transfer)

        self.assertTrue((balance_2_after - balance_2_before) == transfer, assertMessage='Account 2 should receive funds')