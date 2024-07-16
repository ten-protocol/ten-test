import base64, ast, os, secrets
from web3._utils.events import EventLogErrorFlags
from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        transfer = 10000000000000
        user2_pk = secrets.token_hex(32)

        user1 = BridgeUser(self, Properties().account1pk(), Properties().account1pk(), 'user1')
        user2 = BridgeUser(self, user2_pk, user2_pk, 'user2')

        params = {'from': user1.l2.account.address,
                  'chainId': user1.l2.web3.eth.chain_id,
                  'gasPrice': user1.l2.web3.eth.gas_price,
                  'value':transfer}
        gas_limit = user1.l2.bridge.contract.functions.sendNative(user1.l1.account.address).estimate_gas(params)
        nonce1, tx_sign1 = self.create_signed(user2, transfer, gas_limit)
        nonce2, tx_sign2 = self.create_signed(user2, transfer, gas_limit)
        tx_hash1 = self.send_tx(user2, nonce1, tx_sign1)
        tx_hash2 = self.send_tx(user2, nonce2, tx_sign2)
        tx_recp1 = self.wait_tx(user2, nonce2, tx_hash1)
        tx_recp2 = self.wait_tx(user2, nonce2, tx_hash2)

        value_transfer = user2.l2.bus.contract.events.ValueTransfer().process_receipt(tx_recp2, EventLogErrorFlags.Ignore)
        log_message = user2.l2.bus.contract.events.LogMessagePublished().process_receipt(tx_recp2, EventLogErrorFlags.Ignore)

        block = user2.l2.web3.eth.get_block(tx_recp2.blockNumber)
        decoded = ast.literal_eval(base64.b64decode(block.crossChainTree).decode('utf-8'))
        self.log.info('  value_transfer:   %s', list(value_transfer))
        self.log.info('  cross_chain:      %s', decoded)
        self.log.info('  merkle_root:      %s', block.crossChainTreeHash)
        with open(os.path.join(self.output, 'cross_chain.log'), 'w') as fp:
            for entry in decoded: fp.write('%s,%s\n' % (entry[0], entry[1]))

    def create_signed(self, user, amount, gas_limit):
        nonce = user.l2.network.get_next_nonce(self, user.l2.web3, user.l2.account, True, False)
        tx = user.l2.bridge.contract.functions.sendNative(user.l1.account.address).build_transaction(
            {
                'nonce': nonce,
                'chainId': user.l2.web3.eth.chain_id,
                'gas': gas_limit,
                'gasPrice': user.l2.web3.eth.gas_price,
                'value': amount
            }
        )
        tx_sign = user.l2.network.sign_transaction(self, tx, nonce, user.l2.account, True)
        return nonce, tx_sign

    def send_tx(self, user, nonce, tx_sign):
        return user.l2.network.send_transaction(self, user.l2.web3, nonce, user.l2.account, tx_sign, True, False)

    def wait_tx(self, user, nonce, tx_hash, timeout=30):
        return user.l2.network.wait_for_transaction(self, user.l2.web3, nonce, user.l2.account, tx_hash, True, False, timeout)
