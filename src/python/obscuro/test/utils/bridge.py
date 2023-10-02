import time
from web3._utils.events import EventLogErrorFlags
from obscuro.test.contracts.erc20 import ERC20Token
from obscuro.test.contracts.bridge import WrappedERC20
from obscuro.test.contracts.bridge import ObscuroBridge, EthereumBridge
from obscuro.test.contracts.bridge import L1MessageBus, L2MessageBus, L1CrossChainMessenger, L2CrossChainMessenger
from obscuro.test.helpers.log_subscriber import AllEventsLogSubscriber
from obscuro.test.utils.properties import Properties


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

    def wait_for_message(self, xchain_msg, timeout=30):
        """Wait for a cross chain message to be verified as final. """
        start = time.time()
        while True:
            ret = self.bus.contract.functions.verifyMessageFinalized(xchain_msg).call()
            if ret: break
            if time.time() - start > timeout:
                raise TimeoutError('Timed out waiting for message to be verified')
            time.sleep(1.0)

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


class L1BridgeDetails(BridgeDetails):
    """Abstraction over the L1 side of the bridge for a particular account. """

    def __init__(self, test, pk, name):
        """Instantiate an instance. """
        network = test.get_l1_network_connection(verbose=True)
        web3, account = network.connect(test, pk)
        bridge = ObscuroBridge(test, web3)
        bus = L1MessageBus(test, web3)
        xchain = L1CrossChainMessenger(test, web3)
        super().__init__(test, web3, account, network, bridge, bus, xchain, name)
        self.tokens = {}

    def add_token_contract(self, address, name, symbol):
        """Store a reference to the ERC20 token, keyed on its symbol. """
        self.tokens[symbol] = ERC20Token(self.test, self.web3, name, symbol, address)
        return self.tokens[symbol]

    def add_token_subscriber(self, symbol):
        token = self.tokens[symbol]
        subscriber = AllEventsLogSubscriber(self.test, self.network, token,
                                            stdout='l1_sub_%s.out' % self.name, stderr='l1_sub_%s.err' % self.name)
        subscriber.run()

    def transfer_token(self, symbol, to_address, amount):
        """Transfer tokens within the ERC contract from this user account to another address. """
        token = self.tokens[symbol]
        tx_receipt = self.network.transact(self.test, self.web3,
                                           token.contract.functions.transfer(to_address, amount),
                                           self.account, gas_limit=token.GAS_LIMIT, persist_nonce=False)
        return tx_receipt

    def approve_token(self, symbol, approval_address, amount):
        """Approve another address to spend ERC20 on behalf of this account. """
        token = self.tokens[symbol]
        tx_receipt = self.network.transact(self.test, self.web3,
                                           token.contract.functions.approve(approval_address, amount),
                                           self.account, gas_limit=token.GAS_LIMIT, persist_nonce=False)
        return tx_receipt

    def balance_for_token(self, symbol):
        """Get the balance for a token. """
        token = self.tokens[symbol]
        return token.contract.functions.balanceOf(self.account.address).call()

    def white_list_token(self, symbol):
        """Whitelist the ERC20 token for this token to be available on the L2 side of the bridge.

        The account performing the whitelist operation must have admin role access to the bridge.
        """
        token = self.tokens[symbol]
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.bridge.contract.functions.whitelistToken(token.address,
                                                                                         token.name,
                                                                                         token.symbol),
                                           self.account, gas_limit=self.bridge.GAS_LIMIT, persist_nonce=False)
        logs = self.bus.contract.events.LogMessagePublished().processReceipt(tx_receipt, EventLogErrorFlags.Ignore)
        return tx_receipt, self.get_cross_chain_message(logs[1])

    def send_erc20(self, symbol, address, amount):
        """Send tokens across the bridge.

        The ERC20 contract must have been whitelisted for this operation to be successful.
        """
        token = self.tokens[symbol]
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.bridge.contract.functions.sendERC20(token.address,
                                                                                    amount, address),
                                           self.account, gas_limit=self.bridge.GAS_LIMIT, persist_nonce=False)
        logs = self.bus.contract.events.LogMessagePublished().processReceipt(tx_receipt, EventLogErrorFlags.Ignore)
        return tx_receipt, self.get_cross_chain_message(logs[2])

    def send_native(self, address, amount):
        """Send native currency across the bridge."""
        build_tx = self.bridge.contract.functions.sendNative(address).buildTransaction(
            {
                'gas': 4*21000,
                'gasPrice': self.web3.eth.gas_price,
                'value': amount
            }
        )
        tx_receipt = self.network.tx(self.test, self.web3, build_tx, self.account, persist_nonce=False)

        logs = self.bus.contract.events.LogMessagePublished().processReceipt(tx_receipt, EventLogErrorFlags.Ignore)
        return tx_receipt, self.get_cross_chain_message(logs[0])

    def send_to_msg_bus(self, amount):
        """Send native currency across the bridge."""
        tx = {
            'to': Properties().l1_message_bus_address(self.test.env),
            'value': amount,
            'gas': 4*21000,
            'gasPrice': self.web3.eth.gas_price,
        }
        tx_receipt = self.network.tx(self.test, self.web3, tx, self.account, persist_nonce=False)

        logs = self.bus.contract.events.ValueTransfer().processReceipt(tx_receipt, EventLogErrorFlags.Ignore)
        return tx_receipt, logs

    def relay_message(self, xchain_msg):
        """Relay a cross chain message. """
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.xchain.contract.functions.relayMessage(xchain_msg),
                                           self.account, gas_limit=self.xchain.GAS_LIMIT, persist_nonce=False)
        return tx_receipt


class L2BridgeDetails(BridgeDetails):
    """Abstraction of the L2 side of the bridge for a particular address. """

    def __init__(self, test, pk, name):
        """Instantiate an instance. """
        network = test.get_network_connection(name=name, verbose=True)
        web3, account = network.connect(test, pk)
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
        subscriber = AllEventsLogSubscriber(self.test, self.network, token,
                                            stdout='l2_sub_%s.out' % self.name, stderr='l2_sub_%s.err' % self.name)
        subscriber.run()

    def balance_for_token(self, symbol):
        """Get the balance for a token. """
        token = self.tokens[symbol]
        return token.contract.functions.balanceOf(self.account.address).call({"from":self.account.address})

    def relay_whitelist_message(self, xchain_msg):
        """Relay a cross chain message specific to a whitelisting. """
        tx_receipt = self.relay_message(xchain_msg)
        logs = self.bridge.contract.events.CreatedWrappedToken().processReceipt(tx_receipt, EventLogErrorFlags.Ignore)
        return tx_receipt, logs[1]['args']['localAddress']

    def approve_token(self, symbol, approval_address, amount):
        """Approve another address to spend ERC20 on behalf of this account. """
        token = self.tokens[symbol]
        tx_receipt = self.network.transact(self.test, self.web3,
                                           token.contract.functions.approve(approval_address, amount),
                                           self.account, gas_limit=token.GAS_LIMIT)
        return tx_receipt

    def send_erc20(self, symbol, address, amount):
        """Send tokens across the bridge.

        The ERC20 contract must have been whitelisted for this operation to be successful.
        """
        token = self.tokens[symbol]
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.bridge.contract.functions.sendERC20(token.address,
                                                                                    amount, address),
                                           self.account, gas_limit=self.bridge.GAS_LIMIT)
        logs = self.bus.contract.events.LogMessagePublished().processReceipt(tx_receipt, EventLogErrorFlags.Ignore)
        return tx_receipt, self.get_cross_chain_message(logs[1])

    def relay_message(self, xchain_msg):
        """Relay a cross chain message. """
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.xchain.contract.functions.relayMessage(xchain_msg),
                                           self.account, gas_limit=self.xchain.GAS_LIMIT)
        return tx_receipt


class BridgeUser:
    """Abstracts the L1 and L2 sides of the bridge for a user. """
    def __init__(self, test, l1_pk, l2_pk, name):
        self.l1 = L1BridgeDetails(test, l1_pk, name)
        self.l2 = L2BridgeDetails(test, l2_pk, name)
