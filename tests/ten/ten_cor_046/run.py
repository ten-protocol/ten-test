from eth_utils import keccak
from hexbytes import HexBytes
from pysys.constants import LOG_WARN
from pysys.utils.logutils import BaseLogFormatter
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.create2 import Create2Factory, WrappedNative


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the create2 factory contract
        factory = Create2Factory(self, web3)
        factory.get_or_deploy(network, account, persist_nonce=False)

        # compile the wrapped native contract and get the predicted address
        wrapped = WrappedNative(self, web3)
        salt = b'\x00' * 31 + b'\x01'
        init_code = bytes.fromhex(wrapped.bytecode)
        computed_address = keccak(
            b'\xff' + bytes.fromhex(factory.address[2:]) + salt + keccak(init_code)
        )[12:]
        predicted_address = web3.to_checksum_address(computed_address)
        self.log.info('The predicted contract address is: %s' % predicted_address)

        # deploy the contract via create2
        self.deploy_via_factory(network, web3, account, factory, wrapped, salt)

        # assert the computed address is the same as the actual
        self.assertTrue(predicted_address == wrapped.address, assertMessage='Computed address should equal the actual')

    def deploy_via_factory(self, network, web3, account, factory, wrapped, salt):
        target = factory.contract.functions.deploy(HexBytes(wrapped.bytecode), int.from_bytes(salt, 'big'))
        tx_receipt = network.transact(self, web3, target, account, factory.GAS_LIMIT, persist_nonce=False)

        events = factory.contract.events.Deployed().process_receipt(tx_receipt)
        if events:
            wrapped.account = account
            wrapped.address = events[0]['args']['addr']
            wrapped.contract = web3.eth.contract(address=wrapped.address, abi=wrapped.abi)
            self.log.info('Contract %s deployed at %s', wrapped.CONTRACT, wrapped.address, extra=BaseLogFormatter.tag(LOG_WARN, 0))
        return tx_receipt


