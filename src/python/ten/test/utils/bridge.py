import time, os, rlp
from web3._utils.events import EventLogErrorFlags
from ten.test.contracts.erc20 import ERC20Token
from ten.test.contracts.bridge import WrappedERC20
from ten.test.contracts.bridge import TenBridge, EthereumBridge, CrossChainManagement
from ten.test.contracts.bridge import L1MessageBus, L2MessageBus, L1CrossChainMessenger, L2CrossChainMessenger
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber

class BridgeDetails:

    def __init__(self, test, web3, account, network, bridge, bus, xchain, name):
        """Instantiate an instance. """
        self.test = test
        self.web3 = web3
        self.account = account
        self.network = network
        self.bridge = bridge
        self.bus = bus
        self.xchain = xchain
        self.name = name

    def wait_for_message(self, xchain_msg, timeout=60):
        """Wait for a cross chain message to be verified as final. """
        start = time.time()
        while True:
            ret = self.bus.contract.functions.verifyMessageFinalized(xchain_msg).call()
            if ret:
                self.test.log.info('Message is verified as finalized')
                break
            if time.time() - start > timeout:
                raise TimeoutError('Timed out waiting for message to be verified')
            time.sleep(1.0)

    def wait_for_proof(self, msg_type, msg_hash, timeout):
        wait_period = 2 if self.test.is_local_ten() else 30
        start_time = time.perf_counter_ns()
        root, proof = None, None
        start = time.time()
        while root is None:
            proof, root = self.test.ten_get_xchain_proof(msg_type, msg_hash)
            if root is not None: break
            if time.time() - start > timeout:
                raise TimeoutError('Timed out waiting for message to be verified')
            time.sleep(wait_period)
        proof = rlp.decode(bytes.fromhex(proof[2:]))
        end_time = time.perf_counter_ns()
        self.test.log.info('Total time waiting for the proof: %.1f secs', (end_time-start_time)/1e9)
        return root, proof

    @classmethod
    def get_cross_chain_message(cls, log):
        """Extract the cross chain message from an event log. """
        message = {
            'sender': log['args']['sender'],
            'sequence': log['args']['sequence'],
            'nonce': log['args']['nonce'],
            'topic': log['args']['topic'],
            'payload': log['args']['payload'],
            'consistencyLevel': log['args']['consistencyLevel']
        }
        return message

    @classmethod
    def get_value_transfer_event(cls, log):
        """Extract the cross chain message from an event log. """
        message = {
            'sender': log['args']['sender'],
            'sequence': log['args']['sequence'],
            'receiver': log['args']['receiver'],
            'amount': log['args']['amount']
        }
        return message


class L1BridgeDetails(BridgeDetails):
    """Abstraction over the L1 side of the bridge for a particular account. """

    def __init__(self, test, pk, name, check_funds=True):
        """Instantiate an instance. """
        network = test.get_l1_network_connection()
        web3, account = network.connect(test, pk, check_funds=check_funds)
        bridge = TenBridge(test, web3)
        bus = L1MessageBus(test, web3)
        xchain = L1CrossChainMessenger(test, web3)
        self.management = CrossChainManagement(test, web3)
        super().__init__(test, web3, account, network, bridge, bus, xchain, name)
        self.tokens = {}

    def add_token_contract(self, address, name, symbol):
        """Store a reference to the ERC20 token, keyed on its symbol. """
        self.tokens[symbol] = ERC20Token(self.test, self.web3, name, symbol, address)
        return self.tokens[symbol]

    def add_token_subscriber(self, symbol):
        token = self.tokens[symbol]
        subscriber = AllEventsLogSubscriber(self.test, self.network, token.address, token.abi_path,
                                            stdout='l1_sub_%s.out' % self.name, stderr='l1_sub_%s.err' % self.name)
        subscriber.run()

    def transfer_token(self, symbol, to_address, amount, timeout=60):
        """Transfer tokens within the ERC contract from this user account to another address. """
        token = self.tokens[symbol]
        tx_receipt = self.network.transact(self.test, self.web3,
                                           token.contract.functions.transfer(to_address, amount),
                                           self.account, gas_limit=token.GAS_LIMIT, persist_nonce=False,
                                           timeout=timeout)
        return tx_receipt

    def approve_token(self, symbol, approval_address, amount, timeout=60):
        """Approve another address to spend ERC20 on behalf of this account. """
        token = self.tokens[symbol]
        tx_receipt = self.network.transact(self.test, self.web3,
                                           token.contract.functions.approve(approval_address, amount),
                                           self.account, gas_limit=token.GAS_LIMIT, persist_nonce=False,
                                           timeout=timeout)
        return tx_receipt

    def balance_for_token(self, symbol):
        """Get the balance for a token. """
        token = self.tokens[symbol]
        return token.contract.functions.balanceOf(self.account.address).call()

    def white_list_token(self, symbol, timeout=60):
        """Whitelist the ERC20 token for this token to be available on the L2 side of the bridge.

        The account performing the whitelist operation must have admin role access to the bridge.
        """
        token = self.tokens[symbol]
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.bridge.contract.functions.whitelistToken(token.address,
                                                                                         token.name,
                                                                                         token.symbol),
                                           self.account, gas_limit=self.bridge.GAS_LIMIT, persist_nonce=False,
                                           timeout=timeout)

        logs = self.bus.contract.events.LogMessagePublished().process_receipt(tx_receipt, EventLogErrorFlags.Discard)
        return tx_receipt, self.get_cross_chain_message(logs[0])

    def send_erc20(self, symbol, address, amount, timeout=60):
        """Send tokens across the bridge.

        The ERC20 contract must have been whitelisted for this operation to be successful.
        """
        token = self.tokens[symbol]
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.bridge.contract.functions.sendERC20(token.address,
                                                                                    amount, address),
                                           self.account, gas_limit=self.bridge.GAS_LIMIT, persist_nonce=False,
                                           timeout=timeout)
        logs = self.bus.contract.events.LogMessagePublished().process_receipt(tx_receipt, EventLogErrorFlags.Discard)
        return tx_receipt, self.get_cross_chain_message(logs[0])

    def send_native(self, address, amount, timeout=60):
        """Send native currency across the bridge."""
        build_tx = self.bridge.contract.functions.sendNative(address).build_transaction(
            {
                'gas': 4*21000,
                'gasPrice': self.web3.eth.gas_price,
                'value': amount,
                'chainId': self.web3.eth.chain_id
            }
        )
        tx_receipt = self.network.tx(self.test, self.web3, build_tx, self.account, persist_nonce=False, timeout=timeout, txstr='sendNative(%d)'%amount)
        self.network.dump(tx_receipt, 'send_native_tx.log')
        logs = self.bus.contract.events.LogMessagePublished().process_receipt(tx_receipt, EventLogErrorFlags.Discard)
        return tx_receipt, self.get_cross_chain_message(logs[0])

    def relay_message(self, xchain_msg, timeout=60):
        """Relay a cross chain message. """
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.xchain.contract.functions.relayMessage(xchain_msg),
                                           self.account, gas_limit=self.xchain.GAS_LIMIT, persist_nonce=False,
                                           timeout=timeout)
        return tx_receipt

    def release_tokens(self, msg, proof, root, timeout=60):
        """Release tokens to an account. """
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.xchain.contract.functions.relayMessageWithProof(msg, proof, root),
                                           self.account, gas_limit=self.xchain.GAS_LIMIT, persist_nonce=False,
                                           timeout=timeout)

        return tx_receipt

    def release_funds(self, msg, proof, root, timeout=60):
        """Release funds to an account. """
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.xchain.contract.functions.relayMessageWithProof(msg, proof, root),
                                           self.account, gas_limit=self.management.GAS_LIMIT, persist_nonce=False,
                                           timeout=timeout)

        return tx_receipt


class L2BridgeDetails(BridgeDetails):
    """Abstraction of the L2 side of the bridge for a particular address. """

    def __init__(self, test, pk, name, check_funds=True):
        """Instantiate an instance. """
        network = test.get_network_connection()
        web3, account = network.connect(test, pk, check_funds=check_funds)
        bridge = EthereumBridge(test, web3)
        bus = L2MessageBus(test, web3)
        xchain = L2CrossChainMessenger(test, web3)
        super().__init__(test, web3, account, network, bridge, bus, xchain, name)
        self.tokens = {}

    def set_token_contract(self, address, name, symbol):
        """Store a reference to the ERC20 token, keyed on its symbol. """
        self.tokens[symbol] = WrappedERC20(self.test, self.web3, name, symbol, address)
        return self.tokens[symbol]

    def add_token_subscriber(self, symbol):
        token = self.tokens[symbol]
        subscriber = AllEventsLogSubscriber(self.test, self.network, token.address, token.abi_path,
                                            stdout='l2_sub_%s.out' % self.name, stderr='l2_sub_%s.err' % self.name)
        subscriber.run()

    def balance_for_token(self, symbol):
        """Get the balance for a token. """
        token = self.tokens[symbol]
        return token.contract.functions.balanceOf(self.account.address).call({"from":self.account.address})

    def send_erc20_fees(self):
        return self.bridge.contract.functions.erc20Fee().call()

    def send_native_fees(self):
        return self.bridge.contract.functions.valueTransferFee().call()

    def relay_whitelist_message(self, xchain_msg, timeout=60, dump_file=None):
        """Relay a cross chain message specific to a whitelisting. """
        tx_receipt = self.relay_message(xchain_msg, timeout=timeout)
        if dump_file: self.network.dump(tx_receipt, dump_file)
        logs = self.bridge.contract.events.CreatedWrappedToken().process_receipt(tx_receipt, EventLogErrorFlags.Discard)
        return tx_receipt, logs[0]['args']['localAddress']

    def approve_token(self, symbol, approval_address, amount, timeout=60, dump_file=None):
        """Approve another address to spend ERC20 on behalf of this account. """
        token = self.tokens[symbol]
        tx_receipt = self.network.transact(self.test, self.web3,
                                           token.contract.functions.approve(approval_address, amount),
                                           self.account, gas_limit=token.GAS_LIMIT,
                                           timeout=timeout)
        if dump_file: self.network.dump(tx_receipt, dump_file)

        return tx_receipt

    def send_erc20(self, symbol, address, amount, timeout=60, dump_file=None):
        """Send tokens across the bridge.

        The ERC20 contract must have been whitelisted for this operation to be successful.
        """
        token = self.tokens[symbol]
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.bridge.contract.functions.sendERC20(token.address, amount, address),
                                           self.account, gas_limit=self.bridge.GAS_LIMIT,
                                           timeout=timeout, value=int(self.send_erc20_fees()))
        if dump_file: self.network.dump(tx_receipt, dump_file)

        logs = self.bus.contract.events.LogMessagePublished().process_receipt(tx_receipt, EventLogErrorFlags.Discard)
        return tx_receipt, self.get_cross_chain_message(logs[0])

    def send_native(self, address, amount, timeout=60, dump_file=None):
        """Send native currency across the bridge."""
        target = self.bridge.contract.functions.sendNative(address)
        params = {'gasPrice': self.web3.eth.gas_price, 'value': amount + int(self.send_native_fees()), 'chainId': self.web3.eth.chain_id}
        params['gas'] = target.estimate_gas(params)
        build_tx = target.build_transaction(params)

        tx_receipt = self.network.tx(self.test, self.web3, build_tx, self.account, timeout=timeout, txstr='sendNative(%d)'%amount)
        if dump_file: self.network.dump(tx_receipt, os.path.join(self.test.output, dump_file))

        logs = self.bus.contract.events.LogMessagePublished().process_receipt(tx_receipt, EventLogErrorFlags.Discard)
        return tx_receipt, self.get_cross_chain_message(logs[0])

    def relay_message(self, xchain_msg, timeout=60, dump_file=None):
        """Relay a cross chain message. """
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.xchain.contract.functions.relayMessage(xchain_msg),
                                           self.account, gas_limit=self.xchain.GAS_LIMIT,
                                           timeout=timeout)
        if dump_file: self.network.dump(tx_receipt, dump_file)
        return tx_receipt


class BridgeUser:
    """Abstracts the L1 and L2 sides of the bridge for a user. """
    def __init__(self, test, l1_pk, l2_pk, name, check_funds=True):
        self.l1 = L1BridgeDetails(test, l1_pk, name, check_funds)
        self.l2 = L2BridgeDetails(test, l2_pk, name, check_funds)
