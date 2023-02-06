import time, os, json
from pysys.constants import PROJECT
from web3._utils.events import EventLogErrorFlags
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.contracts.bridge.bridge import ObscuroBridge, EthereumBridge
from obscuro.test.contracts.bridge.messaging import L1MessageBus, L2MessageBus, CrossChainMessenger


class L1BridgeDetails:
    """Abstraction of the L1 side of the bridge for a particular user. """

    def __init__(self, test, pk):
        self.network = NetworkFactory.get_l1_network(test)
        self.web3, self.account = self.network.connect(self, pk)
        self.bridge = ObscuroBridge(self, self.web3)
        self.bus = L1MessageBus(self, self.web3)
        self.token = None

    def set_token_from_address(self, address):
        """Set the web3 contract instance for the ERC20 token."""
        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as f:
            self.token = self.web3.eth.contract(address=address, abi=json.load(f))

    def transfer_token(self, address, amount):
        """Transfer tokens within the ERC contract from this user to another. """
        tx_receipt =  self.network.transact(self, self.web3,
                                            self.token.contract.functions.transfer(address, amount),
                                            self.account, gas_limit=7200000, persist_nonce=False)
        return tx_receipt

    def approve_token(self, address, amount):
        """Approve another user to spend ERC20 on behalf of this user. """
        tx_receipt = self.network.transact(self, self.web3,
                                           self.token.contract.functions.approve(address, amount),
                                           self.account, gas_limit=7200000, persist_nonce=False)
        return tx_receipt

    def white_list_token(self):
        """Whitelist the token to be available on the L2 side of the bridge. """
        tx_receipt = self.network.transact(self, self.web3,
                                           self.bridge.contract.functions.whitelistToken(self.token.contract_address,
                                                                                         self.token.name,
                                                                                         self.token.symbol),
                                           self.account, gas_limit=7200000, persist_nonce=False)
        logs = self.bus.contract.events.LogMessagePublished().processReceipt(tx_receipt, EventLogErrorFlags.Ignore)
        return tx_receipt, L1BridgeDetails.get_cross_chain_message(logs[1])

    def send_erc20(self, account, amount):
        """Send tokens across the bridge. """
        tx_receipt = self.network.transact(self, self.web3,
                                           self.bridge.contract.functions.sendERC20(self.token.contract_address,
                                                                                    amount, account.address),
                                           self.account, gas_limit=7200000, persist_nonce=False)
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
    """Abstraction of the L2 side of the bridge for a particular user. """

    def __init__(self, test, pk):
        self.network = NetworkFactory.get_network(test)
        self.web3, self.account = self.network.connect(self, pk)
        self.bridge = EthereumBridge(self, self.web3)
        self.bus = L2MessageBus(self, self.web3)
        self.xchain = CrossChainMessenger(self, self.web3)
        self.token = None

    def set_token_from_address(self, address):
        """Set the web3 contract instance for the ERC20 token."""
        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as f:
            self.token = self.web3.eth.contract(address=address, abi=json.load(f))

    def wait_for_message(self, xchain_msg, timeout=30):
        """Wait for a cross chain message to tbe verified as final. """
        start = time.time()
        while True:
            ret = self.bus.contract.functions.verifyMessageFinalized(xchain_msg).call()
            if ret: break
            if time.time() - start > timeout:
                raise TimeoutError('Timed out waiting for message to be verified')
            time.sleep(1.0)

    def relay_message(self, xchain_msg):
        """Relay a cross chain message. """
        tx_receipt = self.network.transact(self, self.web3,
                                           self.network.xchain.contract.functions.relayMessage(xchain_msg),
                                           self.network.account, gas_limit=7200000, persist_nonce=False)
        logs = self.bridge.contract.events.CreatedWrappedToken().processReceipt(tx_receipt, EventLogErrorFlags.Ignore)
        return tx_receipt, logs

    def relay_whitelist_message(self, xchain_msg):
        """Relay a cross chain message specific to a whitelisting. """
        tx_receipt, logs = self.relay_message(xchain_msg)
        l2_token_address = logs[1]['args']['localAddress']
        return tx_receipt, l2_token_address


class BridgeUser:
    """Abstracts the L1 and L2 sides of the bridge for a user. """
    def __init__(self, test, l1_pk, l2_pk):
        self.l1 = L1BridgeDetails(test, l1_pk)
        self.l2 = L2BridgeDetails(test, l2_pk)
