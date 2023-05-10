import json
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.relevancy import Relevancy
from obscuro.test.contracts.payable import ReceiveEther, SendEther
from obscuro.test.contracts.storage import Storage, KeyStorage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # clear the stored contract addresses for a new environment
        self.contract_db.delete(self.env)

        # connect to network
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # deploy the storage contract
        contracts = []
        contracts.append(Storage(self, web3, 250))
        contracts.append(KeyStorage(self, web3))
        contracts.append(Relevancy(self, web3))
        contracts.append(ReceiveEther(self, web3))
        contracts.append(SendEther(self, web3))

        for contract in contracts:
            self.log.info("")
            contract.deploy(network, account)
            self.log.info('Deployed %s contract to address %s' % (contract.CONTRACT, contract.address))
            self.contract_db.insert(contract.CONTRACT, self.env, contract.address, json.dumps(contract.abi))
