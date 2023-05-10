import json
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage import Storage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self)
        web3_1, account1 = network.connect_account1(self)

        # deploy the contract
        storage = Storage(self, web3_1, 100)
        storage.deploy(network, account1)

        # save the contract details to the persistence file
        self.contract_db.insert(storage.CONTRACT, self.env, storage.address, json.dumps(storage.abi))
