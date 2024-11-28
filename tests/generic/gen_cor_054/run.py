from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.error import Error


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network, deploy the error contract and then estimate gas for the test
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        error = Error(self, web3)
        error.deploy(network, account)

        chain_id = web3.eth.chain_id
        gas_price = web3.eth.gas_price
        target_fn = error.contract.functions.set_key_with_revert
        params = {'nonce': 0, 'gasPrice': gas_price, 'chainId': chain_id}
        gas_estimate = target_fn("one").estimate_gas(params)

        # use an ephemeral account and give it funds
        funds_needed = 10*(gas_estimate * gas_price)
        web3, account = network.connect(self, private_key=self.get_ephemeral_pk(), check_funds=False)
        self.distribute_native(account, web3.from_wei(funds_needed, 'ether'))

        # pre-sign, bulk send, and then wait for the tx with the highest nonce
        self.log.info('Creating signed transactions')
        signed_txs = []
        signed_txs.append(self.submit(account, target_fn('thr'), 3, gas_price, gas_estimate, chain_id))
        signed_txs.append(self.submit(account, target_fn('two'), 2, gas_price, gas_estimate, chain_id))
        signed_txs.append(self.submit(account, target_fn('zer'), 1, gas_price, gas_estimate, chain_id))
        signed_txs.append(self.submit(account, target_fn(''), 0, gas_price, gas_estimate, chain_id))

        self.log.info('Bulk sending signed transactions')
        tx_hashes = [web3.eth.send_raw_transaction(x.rawTransaction) for x in signed_txs]

        self.log.info('Waiting for the tx receipt for the highest nonce')
        for tx_hash in tx_hashes:
            try:
                tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash.hex(), timeout=30)
                self.log.info(tx_receipt)
            except:
                self.log.warn('Exception raised')

        self.assertTrue(error.contract.functions.get_key().call() == 'thr')

    def submit(self, account, target, nonce, gas_price, gas_limit, chain_id):
        build_tx = target.build_transaction({
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas_limit,
            'chainId': chain_id
        })
        return account.sign_transaction(build_tx)


