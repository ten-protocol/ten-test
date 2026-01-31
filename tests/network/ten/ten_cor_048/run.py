from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties
from ten.test.helpers.merkle_tree import MerkleTreeHelper


class PySysTest(TenNetworkTest):
    sym = 'WETH'
    amount_over = 10_000
    amount_back = 2_000
    proof_timeout = 90

    def execute(self):
        props = Properties()

        # create the users for the test
        accnt1 = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')

        # check the weth balance and deposit some more if required
        self.log.info('')
        self.log.info('Deposit WETH (units are in wei)')
        balance = accnt1.l1.balance_for_token(self.sym)
        self.log.info('Account1 ERC20 balance before = %d ', balance)
        if balance < 1_000_000:
            accnt1.l1.deposit_weth(1_000_000)
            self.log.info('Account1 ERC20 balance after  = %d ', accnt1.l1.balance_for_token(self.sym))
        else:
            self.log.info('Sufficient balance exists in weth on this account')

        # check how much the bridge is approved to spend for the account and approve more if required
        self.log.info('')
        self.log.info('Approve WETH on the L1')
        allowance = accnt1.l1.allowance_for_token(self.sym, accnt1.l1.bridge.address)
        self.log.info('Account1 WETH bridge allowance before = %d ', allowance)
        if allowance < 100_000:
            accnt1.l1.approve_token(self.sym, accnt1.l1.bridge.address, 100_000)
            self.log.info('Account1 WETH bridge allowance after  = %d ', accnt1.l1.allowance_for_token(self.sym, accnt1.l1.bridge.address))
        else:
            self.log.info('Sufficient allowance exists in WETH on this account')

        # send some tokens across the bridge L1 to L2
        self.log.info('')
        self.log.info('Initial balances')
        balance_l1_before = accnt1.l1.balance_for_token(self.sym)
        balance_l2_before = accnt1.l2.balance_for_token(self.sym)
        self.log.info('    Account1 WETH balance L1 = %d ', balance_l1_before)
        self.log.info('    Account1 WETH balance L2 = %d ', balance_l2_before)

        self.log.info('')
        self.log.info('Send WETH on the L1 to cross the bridge')
        _, xchain_msg = accnt1.l1.send_erc20(self.sym, accnt1.l2.account.address, self.amount_over, xchain_pos=1)
        accnt1.l2.wait_for_message(xchain_msg)

        self.log.info('Relay the WETH tokens request')
        _ = accnt1.l2.relay_message(xchain_msg)

        # print out the balances and perform test validation
        self.log.info('')
        self.log.info('Balances after L1 to L2')
        balance_l1_first = accnt1.l1.balance_for_token(self.sym)
        balance_l2_first = accnt1.l2.balance_for_token(self.sym)
        self.log.info('    Account1 WETH balance L1 = %d ', balance_l1_first)
        self.log.info('    Account1 WETH balance L2 = %d ', balance_l2_first)
        self.assertTrue(balance_l1_first == balance_l1_before - self.amount_over)
        self.assertTrue(balance_l2_first == balance_l2_before + self.amount_over)

        # check how much the bridge is approved to spend on the L2 for the account and approve more if required
        self.log.info('')
        self.log.info('Approve WETH on the L2')
        allowance = accnt1.l2.allowance_for_token(self.sym, accnt1.l2.bridge.address)
        self.log.info('Account1 WETH bridge allowance before = %d ', allowance)
        if allowance < 100_000:
            accnt1.l2.approve_token(self.sym, accnt1.l2.bridge.address, 100_000)
            self.log.info('Account1 WETH bridge allowance after  = %d ', accnt1.l2.allowance_for_token(self.sym, accnt1.l2.bridge.address))
        else:
            self.log.info('Sufficient allowance exists in WETH on this account')

        # send some tokens across the bridge L2 to L1
        self.log.info('')
        self.log.info('Send WETH on the L2 to cross the bridge')
        tx_receipt, log_msg = accnt1.l2.send_erc20(self.sym, accnt1.l2.account.address, self.amount_back,
                                                   dump_file='l2_send_erc20.log', xchain_pos=1, fee_multiplier=2)

        # get the log msg from the merkle tree helper
        mh = MerkleTreeHelper.create(self)
        msg, msg_hash = mh.process_log_msg(log_msg)
        block, decoded = mh.dump_tree(accnt1.l2.web3, tx_receipt, 'xchain_tree.log')
        self.log.info('  value_transfer:        %s', msg)
        self.log.info('  value_transfer_hash:   %s', msg_hash)
        self.log.info('  decoded_cross_chain:   %s', decoded)
        self.log.info('  block_merkle_root:     %s', block.crossChainTreeHash)
        self.assertTrue(msg_hash in [x[1] for x in decoded], assertMessage='Value transfer should be in the xchain tree')

        mh_root, mh_proof = mh.get_proof('xchain_tree.log', 'm,%s' % msg_hash)
        self.log.info('  calculated root:       %s', mh_root)
        self.assertTrue(block.crossChainTreeHash == mh_root, assertMessage='Calculated merkle root should be same as the block header')

        # if a local testnet wait for the xchain message on the L1 and release the funds
        if self.is_local_ten(): timeout = self.proof_timeout
        else: timeout = 60*60*7 # need to wait the rollup period

        self.log.info('Getting root and proof for first transaction')
        root, proof = accnt1.l2.wait_for_proof('m', msg_hash, timeout)
        self.log.info('  Returned root:         %s', root)
        self.log.info('  Returned proof:        %s', [p.hex() for p in proof])

        # release the tokens from the L1 and check the balances
        self.log.info('Relay the message on the L1 to release them')
        _ = accnt1.l1.release_tokens(msg, proof, root, timeout=timeout)
        self.wait(30.0)

        # print out the balances and perform test validation
        self.log.info('')
        self.log.info('Balances after L2 to L1')
        balance_l1_second = accnt1.l1.balance_for_token(self.sym)
        balance_l2_second = accnt1.l2.balance_for_token(self.sym)
        self.log.info('  Account1 WETH balance L1 = %d ', balance_l1_second)
        self.log.info('  Account1 WETH balance L2 = %d ', balance_l2_second)
        self.assertTrue(balance_l1_second == balance_l1_before - self.amount_over + self.amount_back)
        self.assertTrue(balance_l2_second == balance_l2_before + self.amount_over - self.amount_back)