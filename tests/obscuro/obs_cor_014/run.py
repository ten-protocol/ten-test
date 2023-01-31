import os
from web3._utils.events import EventLogErrorFlags
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.erc20.erc20 import ERC20Token
from obscuro.test.contracts.bridge.obscuro_bridge import ObscuroBridge
from obscuro.test.contracts.messaging.message_bus import MessageBus
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        block_time = Properties().block_time_secs(self.env)

        # connect and deploy our own ERC20 contract
        l1 = NetworkFactory.get_l1_network(self)
        web3_l1, account_l1 = l1.connect(self, Properties().l1_funded_account_pk(self.env))

        l2 = NetworkFactory.get_network(self)
        web3_l2, account_l2 = l2.connect_account1(self)

        token = ERC20Token(self, web3_l2, 'DodgyCoin', 'DCX')
        token.deploy(l2, account_l2)
        self.wait(float(block_time) * 1.1)
        self.log.info('ERC20 deployed with address %s' % token.contract_address)

        # create the contract instances for both sides of the bridge
        l1_bridge = ObscuroBridge(self, web3_l1)
        message_bus = MessageBus(self, web3_l1)

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

        # log out the details
        log = logs[1]
        exprList = []
        exprList.append('Sender = %s' % log['args']['sender'])
        exprList.append('Sequence = %s' % log['args']['sequence'])
        exprList.append('Nonce = %s' % log['args']['nonce'])
        exprList.append('Topic = %s' % log['args']['topic'])
        exprList.append('ConsistencyLevel = %s' % log['args']['consistencyLevel'])
        self.assertOrderedGrep(file=os.path.join(self.output, 'subscriber.out'), exprList=exprList)





