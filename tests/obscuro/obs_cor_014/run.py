import os
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.erc20.erc20 import ERC20Token
from obscuro.test.contracts.bridge.ethereum_bridge import EthereumBridge
from obscuro.test.contracts.bridge.obscuro_bridge import ObscuroBridge
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
        l2_bridge = EthereumBridge(self, web3_l2)

        # run test specific event subscriber
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'log_msg_subscriber.js')
        args = []
        args.extend(['--network_ws', '%s' % l1.connection_url(web_socket=True)])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Subscribed for event logs', timeout=10)

        # whitelist the token
        tx_receipt = l1.transact(self, web3_l1,
                    l1_bridge.contract.functions.whitelistToken(token.contract_address, 'DodgyCoin', 'DCX'),
                    account_l1, gas_limit=7200000, persist_nonce=False)
        self.log.info(tx_receipt)
        tx_log = l1_bridge.contract.events.LogMessagePublished().processReceipt(tx_receipt)[0]
        self.wait(10.0)

        mapping = l2_bridge.contract.functions.remoteToLocalToken(token.contract_address).call()
        self.log.info('Mapping called returned %s' % mapping)




               AttributeDict({'blockHash': HexBytes('0x1f5412610d28e62f92c30a84895cb7f320cddcde69cfa763b0e060f0d5dfdf0a'),
                              'blockNumber': 56362,
                              'contractAddress': None,
                              'cumulativeGasUsed': 76209,
                              'effectiveGasPrice': 1000,
                              'from': '0x13E23Ca74DE0206C56ebaE8D51b5622EFF1E9944',
                              'gasUsed': 76209,
                              'logs': [
                                       AttributeDict({'address': '0x26c62148Cf06C9742b8506A2BCEcd7d72E51A206', 'topics': [HexBytes('0x2f8788117e7eff1d82e926ec794901d17c78024a50270940304540a733656f0d'), HexBytes('0x9f225881f6e7ac8a885b63aa2269cbce78dd6a669864ccd2cd2517a8e709d73a'), HexBytes('0x000000000000000000000000099326e60778efeb208ed9dd508b417309f3b183'), HexBytes('0x00000000000000000000000013e23ca74de0206c56ebae8d51b5622eff1e9944')], 'data': '0x', 'blockNumber': 56362, 'transactionHash': HexBytes('0xeb1a5726b1942f0696165b6621dcfb9fa5551a566bec3a389615afc50ac7bb62'), 'transactionIndex': 0, 'blockHash': HexBytes('0x1f5412610d28e62f92c30a84895cb7f320cddcde69cfa763b0e060f0d5dfdf0a'), 'logIndex': 0, 'removed': False}),
                                       AttributeDict({'address': '0xFD03804faCA2538F4633B3EBdfEfc38adafa259B', 'topics': [HexBytes('0xb93c37389233beb85a3a726c3f15c2d15533ee74cb602f20f490dfffef775937')], 'data': '0x00000000000000000000000026c62148cf06c9742b8506a2bcecd7d72e51a20600000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001a00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000907343626274bba0858073c67b4d40b87c656c870000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e4458ffd63000000000000000000000000099326e60778efeb208ed9dd508b417309f3b183000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000009446f646779436f696e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003444358000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000', 'blockNumber': 56362, 'transactionHash': HexBytes('0xeb1a5726b1942f0696165b6621dcfb9fa5551a566bec3a389615afc50ac7bb62'), 'transactionIndex': 0, 'blockHash': HexBytes('0x1f5412610d28e62f92c30a84895cb7f320cddcde69cfa763b0e060f0d5dfdf0a'), 'logIndex': 1, 'removed': False})],
                              'logsBloom': HexBytes('0x00000004000000000000000000000000000000000000000000000000000000000000001000000000000000000010020000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000000008000080000000000000081000000000000000000000000000000000000000000000000000000000000000000003000000000000100000008000000000000000108000000000000000040000100000000000000000000000000000000000000000000001010000004000000000000000000000000'),
                              'status': 1,
                              'to': '0x26c62148Cf06C9742b8506A2BCEcd7d72E51A206',
                              'transactionHash': HexBytes('0xeb1a5726b1942f0696165b6621dcfb9fa5551a566bec3a389615afc50ac7bb62'),
                              'transactionIndex': 0,
                              'type': '0x0'})