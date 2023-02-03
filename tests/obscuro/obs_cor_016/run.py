import time, os, json
from pysys.constants import PROJECT
from web3._utils.events import EventLogErrorFlags
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.erc20.minted_erc20 import MintedERC20Token
from obscuro.test.contracts.bridge.bridge import ObscuroBridge, EthereumBridge
from obscuro.test.contracts.bridge.messaging import L1MessageBus, L2MessageBus, CrossChainMessenger
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):
    ERC20_NAME = 'SmartyCoin'
    ERC20_SYMB = 'SCN'

    def execute(self):
        # connect pre-funded and user accounts to the L1 and L2
        l1 = NetworkFactory.get_l1_network(self)
        l2 = NetworkFactory.get_network(self)
        l1_web3_fund, l1_account_fund = l1.connect(self, Properties().l1_funded_account_pk(self.env))
        l2_web3_fund, l2_account_fund = l2.connect(self, Properties().l2_funded_account_pk(self.env))
        l1_web3_user, l1_account_user = l1.connect(self, Properties().account1pk())
        l2_web3_user, l2_account_user = l2.connect_account1(self)

        # deploy the ERC20 minted contract to the L1 and allocate some funds to the user account
        # note that we don't use persisted nonces on the L1 when we transact
        _token = MintedERC20Token(self, l1_web3_fund, self.ERC20_NAME, self.ERC20_SYMB, 10000)
        _token.deploy(l1, l1_account_fund, persist_nonce=False)
        l1_token_address = _token.contract_address
        l1.transact(self, l1_web3_fund,
                    _token.contract.functions.transfer(l1_account_user.address, 200),
                    l1_account_fund, gas_limit=7200000, persist_nonce=False)

        # create the contract instances
        l1_bridge_fund = ObscuroBridge(self, l1_web3_fund)
        l1_message_bus_fund = L1MessageBus(self, l1_web3_fund)
        l2_message_bus_fund = L2MessageBus(self, l2_web3_fund)
        l2_bridge_fund = EthereumBridge(self, l2_web3_fund)
        l2_xchain_messenger_fund = CrossChainMessenger(self, l2_web3_fund)

        l1_bridge_user = ObscuroBridge(self, l1_web3_user)

        # whitelist the token, construct the cross chain message and wait for it to be verified as finalised
        # and relay the message to create the wrapped token
        _receipt = l1.transact(
            self, l1_web3_fund,
            l1_bridge_fund.contract.functions.whitelistToken(l1_token_address, self.ERC20_NAME, self.ERC20_SYMB),
            l1_account_fund, gas_limit=7200000, persist_nonce=False)

        _logs = l1_message_bus_fund.contract.events.LogMessagePublished().processReceipt(_receipt, EventLogErrorFlags.Ignore)
        _xchain_msg = self.get_cross_chain_message(_logs[1])
        self.wait_for_message(l2_message_bus_fund, _xchain_msg)

        _receipt = l2.transact(self, l2_web3_fund, l2_xchain_messenger_fund.contract.functions.relayMessage(_xchain_msg),
                                 l2_account_fund, gas_limit=7200000, persist_nonce=False)

        _logs = l2_bridge_fund.contract.events.CreatedWrappedToken().processReceipt(_receipt, EventLogErrorFlags.Ignore)
        l2_token_address = _logs[1]['args']['localAddress']

        # user requests their balance on the L1 and L2 tokens
        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as f:
            abi = json.load(f)
            user_l1_token = l1_web3_user.eth.contract(address=l1_token_address, abi=abi)
            balance = user_l1_token.functions.balanceOf(l1_account_user.address).call()
            self.log.info('  Account1 ERC20 balance L1 = %d ' % balance)

            user_l2_token = l2_web3_user.eth.contract(address=l2_token_address, abi=abi)
            balance = user_l2_token.functions.balanceOf(l2_account_user.address).call({"from":l2_account_user.address})
            self.log.info('  Account1 ERC20 balance L2 = %d ' % balance)

        # user approves on the L1 token the bridge to be able to transfer funds on their behalf
        l1.transact(self, l1_web3_user, user_l1_token.functions.approve(l1_bridge_fund.contract_address, 100),
                    l1_account_user, gas_limit=7200000, persist_nonce=False)
        allowance = user_l1_token.functions.allowance(l1_account_user.address, l1_bridge_fund.contract_address).call()
        self.log.info('Allowance is %s' % allowance)

        # user sends some ERC20 tokens across the bridge (balance should be seen to drop)
        l1.transact(self, l1_web3_user,
                    l1_bridge_user.contract.functions.sendERC20(l1_token_address, 10, l1_account_user.address),
                    l1_account_user, gas_limit=7200000, persist_nonce=False)
        balance = user_l1_token.functions.balanceOf(l1_account_user.address).call()
        self.log.info('  Account1 ERC20 balance L1 = %d ' % balance)

    def wait_for_message(self, l2_message_bus, xchain_msg):
        start = time.time()
        while True:
            ret = l2_message_bus.contract.functions.verifyMessageFinalized(xchain_msg).call()
            self.log.info('Is message verified: %s' % ret)
            if ret: break
            if time.time() - start > 30:
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
