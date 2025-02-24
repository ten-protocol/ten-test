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
        self.log.info('Retrieved value (no GasPrice)     is %d', storage.contract.functions.retrieve().call())
        self.log.info('Retrieved value (double GasPrice) is %d', storage.contract.functions.retrieve().call({'gasPrice':gas_price*2}))
        self.log.info('Retrieved value (half gasPrice)   is %d', storage.contract.functions.retrieve().call({'gasPrice':int(gas_price*0.5)}))

        # connect an unfunded account to the network through it's own gateway
        network_1 = self.get_network_connection(name='local')
        web3_1, account_1 = network_1.connect(self, private_key=self.get_ephemeral_pk(), check_funds=False)
        storage_1 = Storage.clone(web3_1, account_1, storage)
        self.log.info('Retrieved value (no GasPrice)     is %d', storage_1.contract.functions.retrieve().call())
        self.log.info('Retrieved value (double GasPrice) is %d', storage_1.contract.functions.retrieve().call({'gasPrice':gas_price*2}))
        self.log.info('Retrieved value (half gasPrice)   is %d', storage_1.contract.functions.retrieve().call({'gasPrice':int(gas_price*0.5)}))