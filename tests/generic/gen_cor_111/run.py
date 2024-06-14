from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.access import ContractA, ContractB


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contracts
        contractA = ContractA(self, web3)
        contractA.deploy(network, account)
        contractB = ContractB(self, web3)
        contractB.deploy(network, account)

        # set the contractA address on contractB, and then set the contractA value
        network.transact(self, web3, contractB.contract.functions.setContractA(contractA.address), account, contractB.GAS_LIMIT)
        tx_receipt = network.transact(self, web3, contractB.contract.functions.setContractAValue(100),
                                       account, contractB.GAS_LIMIT)
        gas_without = tx_receipt.gasUsed
        self.log.info('Call shows value %d', contractA.contract.functions.getValue().call())
        self.log.info('Without access list gas: %d' % gas_without)

        # Create an access list and repeat
        access_list = [ { 'address': contractA.address, 'storageKeys': []},
                        { 'address': contractB.address, 'storageKeys': []} ]
        tx_receipt = network.transact(self, web3, contractB.contract.functions.setContractAValue(200),
                                      account, contractB.GAS_LIMIT, access_list=access_list)
        gas_with = tx_receipt.gasUsed
        self.log.info('Call shows value %d', contractA.contract.functions.getValue().call())
        self.log.info('With access list gas: %d' % gas_with)
        self.assertTrue(gas_with < gas_without, assertMessage='Gas with access list should be less')
