from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)
        self.log.info('Using account with address %s' % account.address)

        # create the storage contract but don't deploy yet
        storage = Storage(self, web3, 100)

        # estimate the deployment cost
        build_tx = storage.contract.buildTransaction(
            {
                'nonce': web3.eth.get_transaction_count(account.address),
                'gasPrice': 21000,
                'gas': 720000,
                'chainId': web3.eth.chain_id
            }
        )
        deploy_gas = web3.eth.estimate_gas(build_tx)
        self.log.info('Deployment gas estimate is %d' % deploy_gas)

        # deploy the storage contract
        storage.deploy(network, account)

        # estimate a function call
        store_gas = storage.contract.functions.store(200).estimate_gas()
        retrieve_gas = storage.contract.functions.retrieve().estimate_gas()
        self.log.info('Store gas estimate is %d' % store_gas)
        self.log.info('Retrieve gas estimate is %d' % retrieve_gas)

        # we would expect the cost to deploy to be higher that the cost to store,
        # and the cost of store to be higher than retrieve
        self.assertTrue(deploy_gas > store_gas)
        self.assertTrue(store_gas > retrieve_gas)
