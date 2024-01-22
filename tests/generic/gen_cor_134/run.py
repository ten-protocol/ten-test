from pysys.constants import PASSED, FAILED
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):
    REFERENCE = 24000

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        self.log.info('Using account with address %s', account.address)

        # create the storage contract
        self.log.info('Deploying the storage contract')
        b1 = web3.eth.get_balance(account.address)
        storage = Storage(self, web3, 100)

        # estimate and perform deployment
        self.log.info('Build the transaction to delete the contract')
        build_tx = storage.contract.buildTransaction(
            {
                'nonce': web3.eth.get_transaction_count(account.address),
                'gasPrice': web3.eth.gas_price,
                'gas': Storage.GAS_LIMIT,
                'chainId': web3.eth.chain_id
            }
        )

        self.log.info('Estimate the gas')
        deploy_gas = web3.eth.estimate_gas(build_tx)
        self.log.info('Deployment gas estimate is %d', deploy_gas)

        tx = storage.deploy(network, account)
        b2 = web3.eth.get_balance(account.address)
        self.log.info('TX cost of deployment:        %d', int(tx["gasUsed"]))
        self.log.info('Actual cost of deployment:    %d', (b1-b2))  # gas units * gas price (1000 by default)

        # estimate and perform destruction
        est_1 = storage.contract.functions.destroy().estimate_gas({"from":account.address})
        self.log.info("Estimate destruction:         %d", est_1)

        tx = network.transact(self, web3, storage.contract.functions.destroy(), account, storage.GAS_LIMIT)
        b3 = web3.eth.get_balance(account.address)
        self.log.info('TX cost of destruction:       %d', int(tx["gasUsed"]))
        self.log.info('Actual cost of destruction:   %d', (b3-b2))  # gas units * gas price (1000 by default)
        self.percentile_difference('destroy', int(tx["gasUsed"]), self.REFERENCE, 50)

    def percentile_difference(self, text, result, reference, tolerance):
        percentile = abs(((reference - result) / reference) * 100)
        if percentile >= tolerance:
            self.log.error('Percentile difference for %s is %d (%d compared to %d)', text, percentile, result, reference)
            self.addOutcome(FAILED)
        else:
            self.addOutcome(PASSED)