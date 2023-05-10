import json
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage import Storage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        cursor = self.contract_db.get_contract(Storage.CONTRACT, self.env)
        if len(cursor) > 0:
            address = cursor[0][0]
            abi = cursor[0][1]
            self.log.info('Using pre-deployed contract at address %s' % address)
            contract = web3.eth.contract(address=address, abi=abi)

        else:
            # deploy the contract
            storage = Storage(self, web3, 100)
            storage.deploy(network, account)
            contract = storage.contract

            # save the contract details to the persistence file
            self.contract_db.insert(storage.CONTRACT, self.env, storage.address, json.dumps(storage.abi))

        # retrieve the current value
        value = contract.functions.retrieve().call()
        self.log.info('Call shows value %d' % value)

        # set the value via a transaction and retrieve the new value
        network.transact(self, web3, contract.functions.store(value+1), account, Storage.GAS_LIMIT)
        value_after = contract.functions.retrieve().call()
        self.log.info('Call shows value %d' % value_after)

        # perform assert
        self.assertTrue(value_after == value+1)