import time
from web3._utils.events import EventLogErrorFlags
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.erc20.minted_erc20 import MintedERC20Token
from obscuro.test.contracts.bridge.bridge import ObscuroBridge, EthereumBridge
from obscuro.test.contracts.bridge.messaging import L1MessageBus, L2MessageBus, CrossChainMessenger
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):
    ERC20_NAME = 'DodgyCoin'
    ERC20_SYMB = 'DCX'

    def execute(self):
        # connect and deploy our own ERC20 contract to the L1
        l1 = NetworkFactory.get_l1_network(self)
        l2 = NetworkFactory.get_network(self)
        web3_l1, account_l1 = l1.connect(self, Properties().l1_funded_account_pk(self.env))
        web3_l2, account_l2 = l2.connect(self, Properties().l2_funded_account_pk(self.env))

        token = MintedERC20Token(self, web3_l1, 'DodgyCoin', 'DCX', 10000)
        token.deploy(l1, account_l1, persist_nonce=False) # don't persist nonce on l1

        # create the contract instances
        l1_bridge = ObscuroBridge(self, web3_l1)
        l1_message_bus = L1MessageBus(self, web3_l1)
        l2_message_bus = L2MessageBus(self, web3_l2)
        l2_bridge = EthereumBridge(self, web3_l2)
        l2_xchain_messenger = CrossChainMessenger(self, web3_l2)

        # whitelist the token and extract the log message that is published by the message bus
        tx_receipt = l1.transact(self, web3_l1,
                                 l1_bridge.contract.functions.whitelistToken(token.contract_address, 'DodgyCoin', 'DCX'),
                                 account_l1, gas_limit=7200000, persist_nonce=False)
        logs = l1_message_bus.contract.events.LogMessagePublished().processReceipt(tx_receipt, EventLogErrorFlags.Ignore)

        # construct the cross chain message and wait for it to be verified as finalised
        xchain_msg = self.get_cross_chain_message(logs[1])
        self.wait_for_message(l2_message_bus, xchain_msg)

        # relay the message to the L2 bridge
        tx_receipt = l2.transact(self, web3_l2, l2_xchain_messenger.contract.functions.relayMessage(xchain_msg),
                                 account_l2, l2_xchain_messenger.GAS_LIMIT, persist_nonce=False)
        logs = l2_bridge.contract.events.CreatedWrappedToken().processReceipt(tx_receipt, EventLogErrorFlags.Ignore)

        # log and validate
        log = logs[1]
        self.log.info('RemoteAddress = %s' % log['args']['remoteAddress'])
        self.log.info('LocalAddress = %s' % log['args']['localAddress'])
        self.log.info('Name = %s' % log['args']['name'])
        self.log.info('Symbol = %s' % log['args']['symbol'])

        self.assertTrue(log['args']['remoteAddress'] == token.contract_address)
        self.assertTrue(log['args']['name'] == self.ERC20_NAME)
        self.assertTrue(log['args']['symbol'] == self.ERC20_SYMB)

    def wait_for_message(self, l2_message_bus, xchain_msg):
        start = time.time()
        while True:
            ret = l2_message_bus.contract.functions.verifyMessageFinalized(xchain_msg).call()
            self.log.info('Is message verified: %s' % ret)
            if ret: break
            if time.time() - start > 10:
                raise TimeoutError('Timed out waiting for message to be verified')
            time.sleep(1.0)

    def get_cross_chain_message(self, log):
        message = {
            'sender': log['args']['sender'],
            'sequence': log['args']['sequence'],
            'nonce': log['args']['nonce'],
            'topic': log['args']['topic'],
            'payload': log['args']['payload'],
            'consistencyLevel': log['args']['consistencyLevel']
        }
        return message



