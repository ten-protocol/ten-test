import os
from web3._utils.events import EventLogErrorFlags
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.erc20.minted_erc20 import MintedERC20Token
from obscuro.test.contracts.bridge.bridge import ObscuroBridge
from obscuro.test.contracts.bridge.messaging import L1MessageBus
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        # connect and deploy our own ERC20 contract to the L1
        l1 = NetworkFactory.get_l1_network(self)
        web3_l1, account_l1 = l1.connect(self, Properties().l1_funded_account_pk(self.env))

        token = MintedERC20Token(self, web3_l1, 'DodgyCoin', 'DCX', 10000)
        token.deploy(l1, account_l1, persist_nonce=False) # don't persist nonce on l1

        # create the contract instances
        l1_bridge = ObscuroBridge(self, web3_l1)
        message_bus = L1MessageBus(self, web3_l1)

        # run test specific event subscriber
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'log_msg_subscriber.js')
        args = []
        args.extend(['--network_ws', '%s' % l1.connection_url(web_socket=True)])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Subscribed for event logs', timeout=10)

        # whitelist the token and extract the log message that is published by the message bus
        tx_receipt = l1.transact(self, web3_l1,
                    l1_bridge.contract.functions.whitelistToken(token.contract_address, 'DodgyCoin', 'DCX'),
                    account_l1, gas_limit=7200000, persist_nonce=False)
        logs = message_bus.contract.events.LogMessagePublished().processReceipt(tx_receipt, EventLogErrorFlags.Ignore)

        # verify consistency
        log = logs[1]
        exprList = []
        exprList.append('Sender = %s' % log['args']['sender'])
        exprList.append('Sequence = %s' % log['args']['sequence'])
        exprList.append('Nonce = %s' % log['args']['nonce'])
        exprList.append('Topic = %s' % log['args']['topic'])
        exprList.append('ConsistencyLevel = %s' % log['args']['consistencyLevel'])
        self.assertOrderedGrep(file=os.path.join(self.output, 'subscriber.out'), exprList=exprList)





