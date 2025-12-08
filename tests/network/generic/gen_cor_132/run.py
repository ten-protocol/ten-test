from ten.test.contracts.storage import Storage
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect a funded account to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        gas_price = web3.eth.gas_price

        # deploy the contract and make some calls
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT)

        # connect an unfunded account to the network through it's own gateway
        network_1 = self.get_network_connection(name='local')
        web3_1, account_1 = network_1.connect(self, private_key=self.get_ephemeral_pk(), check_funds=False)
        storage_1 = Storage.clone(web3_1, account_1, storage)
        value = storage_1.contract.functions.retrieve().call()
        self.log.info('Retrieved value (no gasPrice) is %d', value)

        try:
            value = storage_1.contract.functions.retrieve().call({'gasPrice':gas_price})
            self.log.info('Retrieved value (with gasPrice) is %d', value)
        except Exception as e:
            self.assertTrue(type(e) is ValueError, assertMessage='ValueError should be thrown')
            self.log.info('Exception message;')
            self.log.info('  %s' % e.args[0]['message'])

        estimate_gas = storage_1.contract.functions.retrieve().estimate_gas()
        self.log.info('Estimate gas (no gasPrice) is %d' % estimate_gas)
        try:
            estimate_gas = storage_1.contract.functions.retrieve().estimate_gas({'gasPrice':gas_price})
            self.log.info('Estimate gas (with gasPrice) is %d' % estimate_gas)
        except Exception as e:
            self.assertTrue(type(e) is ValueError, assertMessage='ValueError should be thrown')
            self.log.info('Exception message;')
            self.log.info('  %s' % e.args[0]['message'])