import json
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage import Storage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # clear the stored contract addresses for a new environment
        self.contract_db.delete(self.env)

        # connect to network
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        self.log.info('Deployed %s contract to address %s' % (Storage.CONTRACT, storage.address))
        self.contract_db.insert(storage.CONTRACT, self.env, storage.address, json.dumps(storage.abi))
