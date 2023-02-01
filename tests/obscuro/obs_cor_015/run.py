from web3._utils.events import EventLogErrorFlags
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.erc20.erc20 import ERC20Token
from obscuro.test.contracts.bridge.obscuro_bridge import ObscuroBridge
from obscuro.test.contracts.messaging.message_bus import MessageBus
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        # connect and deploy our own ERC20 contract to the L1
        l1 = NetworkFactory.get_l1_network(self)
        web3_l1, account_l1 = l1.connect(self, Properties().l1_funded_account_pk(self.env))

        token = ERC20Token(self, web3_l1, 'DodgyCoin', 'DCX')
        token.deploy(l1, account_l1, persist_nonce=False)
        self.log.info('ERC20 deployed with address %s' % token.contract_address)

        # create the contract instances
        l1_bridge = ObscuroBridge(self, web3_l1)
        message_bus = MessageBus(self, web3_l1)

        # whitelist the token and extract the log message that is published by the message bus
        tx_receipt = l1.transact(self, web3_l1,
                                 l1_bridge.contract.functions.whitelistToken(token.contract_address, 'DodgyCoin', 'DCX'),
                                 account_l1, gas_limit=7200000, persist_nonce=False)
        logs = message_bus.contract.events.LogMessagePublished().processReceipt(tx_receipt, EventLogErrorFlags.Ignore)






