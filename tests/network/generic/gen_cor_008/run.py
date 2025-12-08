from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # create the storage contract but don't deploy yet
        storage = Storage(self, web3, 100)

        # estimate the deployment cost (this is for estimate only so don't persist the nonce)
        build_tx = storage.contract.build_transaction({
                'nonce': self.nonce_db.get_next_nonce(self, web3, account.address, self.env, False),
                'gasPrice': web3.eth.gas_price,
                'chainId': web3.eth.chain_id})
        deploy_gas = web3.eth.estimate_gas(build_tx)
        self.log.info('Deployment gas estimate is %d', deploy_gas)

        # deploy the storage contract
        storage.deploy(network, account)

        # estimate a function call
        store_gas = storage.contract.functions.store(200).estimate_gas()
        retrieve_gas = storage.contract.functions.retrieve().estimate_gas()
        self.log.info('Store gas estimate is %d', store_gas)
        self.log.info('Retrieve gas estimate is %d', retrieve_gas)

        # we would expect the cost to deploy to be higher that the cost to store,
        # and the cost of store to be higher than retrieve
        self.assertTrue(deploy_gas > store_gas)
        self.assertTrue(store_gas > retrieve_gas)
