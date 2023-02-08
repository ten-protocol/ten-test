import time
from web3._utils.events import EventLogErrorFlags
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.contracts.erc20.erc20 import ERC20Token
from obscuro.test.contracts.bridge.bridge import ObscuroBridge, EthereumBridge
from obscuro.test.contracts.bridge.messaging import L1MessageBus, L2MessageBus, CrossChainMessenger


class L1BridgeDetails:
    """Abstraction of the L1 side of the bridge for a particular address. """

    def __init__(self, test, pk):
        self.test = test
        self.network = NetworkFactory.get_l1_network(test)
        self.web3, self.account = self.network.connect(test, pk)
        self.bridge = ObscuroBridge(test, self.web3)
        self.bus = L1MessageBus(test, self.web3)
        self.token = None

    def set_token_contract(self, address, name, symbol):
        """Set the web3 contract instance for the ERC20 token."""
        self.token = ERC20Token(self.test, self.web3, name, symbol, address)

    def transfer_token(self, address, amount):
        """Transfer tokens within the ERC contract from this address to another. """
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.token.contract.functions.transfer(address, amount),
                                           self.account, gas_limit=self.token.GAS_LIMIT, persist_nonce=False)
        return tx_receipt

    def approve_token(self, address, amount):
        """Approve another address to spend ERC20 on behalf of this address. """
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.token.contract.functions.approve(address, amount),
                                           self.account, gas_limit=self.token.GAS_LIMIT, persist_nonce=False)
        return tx_receipt

    def white_list_token(self):
        """Whitelist the token to be available on the L2 side of the bridge. """
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.bridge.contract.functions.whitelistToken(self.token.address,
                                                                                         self.token.name,
                                                                                         self.token.symbol),
                                           self.account, gas_limit=self.bridge.GAS_LIMIT, persist_nonce=False)
        logs = self.bus.contract.events.LogMessagePublished().processReceipt(tx_receipt, EventLogErrorFlags.Ignore)
        return tx_receipt, L1BridgeDetails.get_cross_chain_message(logs[1])

    def send_erc20(self, address, amount):
        """Send tokens across the bridge. """
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.bridge.contract.functions.sendERC20(self.token.address,
                                                                                    amount, address),
                                           self.account, gas_limit=self.bridge.GAS_LIMIT, persist_nonce=False)
        logs = self.bus.contract.events.LogMessagePublished().processReceipt(tx_receipt, EventLogErrorFlags.Ignore)
        return tx_receipt, L1BridgeDetails.get_cross_chain_message(logs[2])

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


class L2BridgeDetails:
    """Abstraction of the L2 side of the bridge for a particular address. """

    def __init__(self, test, pk):
        self.test = test
        self.network = NetworkFactory.get_network(test)
        self.web3, self.account = self.network.connect(test, pk)
        self.bridge = EthereumBridge(test, self.web3)
        self.bus = L2MessageBus(test, self.web3)
        self.xchain = CrossChainMessenger(test, self.web3)
        self.token = None

    def set_token_contract(self, address, name, symbol):
        """Set the web3 contract instance for the ERC20 token."""
        self.token = ERC20Token(self.test, self.web3, name, symbol, address)

    def wait_for_message(self, xchain_msg, timeout=30):
        """Wait for a cross chain message to be verified as final. """
        start = time.time()
        while True:
            ret = self.bus.contract.functions.verifyMessageFinalized(xchain_msg).call()
            if ret: break
            if time.time() - start > timeout:
                raise TimeoutError('Timed out waiting for message to be verified')
            time.sleep(1.0)

    def relay_message(self, xchain_msg):
        """Relay a cross chain message. """
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.xchain.contract.functions.relayMessage(xchain_msg),
                                           self.account, gas_limit=self.xchain.GAS_LIMIT)
        return tx_receipt

    def relay_whitelist_message(self, xchain_msg):
        """Relay a cross chain message specific to a whitelisting. """
        tx_receipt = self.relay_message(xchain_msg)
        logs = self.bridge.contract.events.CreatedWrappedToken().processReceipt(tx_receipt, EventLogErrorFlags.Ignore)
        return tx_receipt, logs[1]['args']['localAddress']


class BridgeUser:
    """Abstracts the L1 and L2 sides of the bridge for a user. """
    def __init__(self, test, l1_pk, l2_pk):
        self.l1 = L1BridgeDetails(test, l1_pk)
        self.l2 = L2BridgeDetails(test, l2_pk)
