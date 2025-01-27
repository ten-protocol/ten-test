from web3._utils.events import EventLogErrorFlags
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.erc20 import MintedERC20Token
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties
from ten.test.helpers.merkle_tree import MerkleTreeHelper


class PySysTest(TenNetworkTest):
    NAME = 'MyToken'
    SYMB = 'MYT'

    def execute(self):
        props = Properties()
        proof_timeout = 60 if self.is_local_ten() else 2400
        transfer = 2000000000000000

        # create the users for the test
        funded = BridgeUser(self, props.l1_funded_account_pk(self.env), props.account2pk(), 'funded')
        accnt1 = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')

        # deploy the token, distribute and whitelist
        self.log.info('Deploy the ERC20 token on the L1')
        token = MintedERC20Token(self, funded.l1.web3, self.NAME, self.SYMB, 10000)
        token.deploy(funded.l1.network, funded.l1.account, persist_nonce=False)
        funded.l1.add_token_contract(token.address, self.NAME, self.SYMB)
        accnt1.l1.add_token_contract(token.address, self.NAME, self.SYMB)
        funded.l1.transfer_token(self.SYMB, accnt1.l1.account.address, 200)
        accnt1.l1.approve_token(self.SYMB, accnt1.l1.bridge.address, 100)
        _, xchain_msg = funded.l1.white_list_token(self.SYMB)
        accnt1.l2.wait_for_message(xchain_msg)
        _, l2_token_address = accnt1.l2.relay_whitelist_message(xchain_msg)

        # send some tokens over the bridge L1 to L2
        funded.l2.set_token_contract(l2_token_address, self.NAME, self.SYMB)
        accnt1.l2.set_token_contract(l2_token_address, self.NAME, self.SYMB)
        _, xchain_msg = accnt1.l1.send_erc20(self.SYMB, accnt1.l2.account.address, 10)
        accnt1.l2.wait_for_message(xchain_msg)
        accnt1.l2.relay_message(xchain_msg)
        self.log.info('Account1 ERC20 balance L1 = %d ', accnt1.l1.balance_for_token(self.SYMB))
        self.log.info('Account1 ERC20 balance L2 = %d ', accnt1.l2.balance_for_token(self.SYMB))

        # approve the bridge on the L2 to send tokens in a withdrawal
        self.log.info('Approve the bridge to spend tokens on the L2')
        accnt1.l2.approve_token(self.SYMB, accnt1.l2.bridge.address, 10)

        # create some value transfer transactions but don't send yet
        params = {'from': accnt1.l2.account.address,
                  'chainId': accnt1.l2.web3.eth.chain_id,
                  'gasPrice': accnt1.l2.web3.eth.gas_price,
                  'value':transfer}
        gas_limit = accnt1.l2.bridge.contract.functions.sendNative(accnt1.l1.account.address).estimate_gas(params)
        nonce1, tx_sign1 = self.create_signed(accnt1, transfer, gas_limit)
        nonce2, tx_sign2 = self.create_signed(accnt1, transfer, gas_limit)
        nonce3, tx_sign3 = self.create_signed(accnt1, transfer, gas_limit)
        nonce4, tx_sign4 = self.create_signed(accnt1, transfer, gas_limit)

        # perform some token and value transfer withdrawals
        self.log.info('Withdraw funds and tokens')
        self.send_tx(accnt1, nonce1, tx_sign1)
        self.send_tx(accnt1, nonce2, tx_sign2)
        self.send_tx(accnt1, nonce3, tx_sign3)
        tx_hash = self.send_tx(accnt1, nonce4, tx_sign4)
        _, log_msg1 = accnt1.l2.send_erc20(self.SYMB, accnt1.l1.account.address, 1, dump_file='send1_erc20.tx')
        _, log_msg2 = accnt1.l2.send_erc20(self.SYMB, accnt1.l1.account.address, 2, dump_file='send2_erc20.tx')

        tx_receipt = self.wait_tx(accnt1, nonce4, tx_hash)
        logs = accnt1.l2.bus.contract.events.ValueTransfer().process_receipt(tx_receipt, EventLogErrorFlags.Ignore)
        value_transfer = accnt1.l2.get_value_transfer_event(logs[0])

        # get the log msg from the merkle tree helper
        mh = MerkleTreeHelper.create(self)
        msg1, msg_hash1 = mh.process_log_msg(log_msg1)
        msg2, msg_hash2 = mh.process_log_msg(log_msg2)
        msg3, msg_hash3 = mh.process_transfer(value_transfer)

        self.log.info('Getting root and proof for first token withdrawal')
        root1, proof1 = accnt1.l2.wait_for_proof('m', msg_hash1, proof_timeout)
        self.log.info('  Returned root:         %s', root1)
        self.log.info('  Returned proof:        %s', [p.hex() for p in proof1])

        self.log.info('Getting root and proof for second token withdrawal')
        root2, proof2 = accnt1.l2.wait_for_proof('m', msg_hash2, proof_timeout)
        self.log.info('  Returned root:         %s', root2)
        self.log.info('  Returned proof:        %s', [p.hex() for p in proof2])

        self.log.info('Getting root and proof for value transfer')
        root3, proof3 = accnt1.l2.wait_for_proof('v', msg_hash3, proof_timeout)
        self.log.info('  returned root:         %s', root3)
        self.log.info('  returned proof:        %s', [p.hex() for p in proof3])

        # release the tokens and native funds from the L1 and check the balances
        self.log.info('Relay the message on the L1 to release them')
        _ = accnt1.l1.release_tokens(msg1, proof1, root1)
        _ = accnt1.l1.release_tokens(msg2, proof2, root2)
        _ = accnt1.l1.release_funds(msg3, proof3, root3)

        # print out the balances and perform test validation
        self.log.info('Print out token balances')
        balance_l1 = accnt1.l1.balance_for_token(self.SYMB)
        balance_l2 = accnt1.l2.balance_for_token(self.SYMB)
        self.log.info('  Account1 ERC20 balance L1 = %d ', balance_l1)
        self.log.info('  Account1 ERC20 balance L2 = %d ', balance_l2)
        self.assertTrue(balance_l1 == 197)
        self.assertTrue(balance_l2 == 2)

    def create_signed(self, user, amount, gas_limit):
        nonce = user.l2.network.get_next_nonce(self, user.l2.web3, user.l2.account.address, True, False)
        tx = user.l2.bridge.contract.functions.sendNative(user.l1.account.address).build_transaction(
            {
                'nonce': nonce,
                'chainId': user.l2.web3.eth.chain_id,
                'gas': gas_limit,
                'gasPrice': user.l2.web3.eth.gas_price,
                'value': amount + int(user.l2.send_native_fees())
            }
        )
        tx_sign = user.l2.network.sign_transaction(self, tx, nonce, user.l2.account, True)
        return nonce, tx_sign

    def send_tx(self, user, nonce, tx_sign):
        return user.l2.network.send_transaction(self, user.l2.web3, nonce, user.l2.account.address, tx_sign, True, False)

    def wait_tx(self, user, nonce, tx_hash, timeout=30):
        return user.l2.network.wait_for_transaction(self, user.l2.web3, nonce, user.l2.account.address, tx_hash, True, False, timeout)
