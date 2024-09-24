from ten.test.basetest import TenNetworkTest
from ten.test.contracts.nested import StoreAndRetrieve


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network and deploy the contract
        network_1 = self.get_network_connection()
        network_2 = self.get_network_connection()
        web3_1, account_1 = network_1.connect_account1(self)
        web3_2, account_2 = network_2.connect_account1(self)

        contract_1 = StoreAndRetrieve(self, web3_1)
        contract_1.deploy(network_1, account_1)
        contract_2 = StoreAndRetrieve.clone(web3_2, account_2, contract_1)

        # Store in a loop with increasing response size and retrieve the response
        query_id = 0
        request_data = "Calculate some randon stuff"
        response_result = "thisistherandomstuff"
        for i in range(100, 500, 50):
            self.log.info('Storing query using account 1 with multiplier %d', i)
            query_id = query_id + 1
            target = contract_1.contract.functions.storeQuery(query_id, request_data, response_result, i)
            network_1.transact(self, web3_1, target, account_1, contract_1.GAS_LIMIT)

            self.log.info('Retrieving query using account 2')
            response = contract_2.contract.functions.retrieveQuery(query_id).call()
            self.assertTrue(response[1][1] == i*response_result)
