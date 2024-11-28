from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.relevancy import Relevancy, RelevancyTwoPhase
from ten.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the storage and storage contract with two phase commit
        relevancy_two_phase = RelevancyTwoPhase(self, web3, Properties().L2PublicCallbacks)
        relevancy_two_phase.deploy(network, account)
        relevancy_normal = Relevancy(self, web3)
        relevancy_normal.deploy(network, account)

        # run the javascript event log subscriber in the background
        subscriber = FilterLogSubscriber(self, network)
        subscriber.run(
            filter_topics=[web3.keccak(text='NonIndexedAddressAndNumber(address,uint256)').hex()]
        )
        subscriber.subscribe()

        # perform some transactions on both contracts
        for i in range(0, 5): self.transact(relevancy_two_phase, web3, network, account)
        network.transact(self, web3, relevancy_normal.contract.functions.nonIndexedAddressAndNumber(account.address),
                         account, relevancy_normal.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)


    def transact(self, relevancy, web3, network, account):
        target = relevancy.contract.functions.nonIndexedAddressAndNumber(account.address)
        params = {'gasPrice': web3.eth.gas_price, 'value': web3.to_wei(0.01, 'ether')}
        gas_estimate = target.estimate_gas(params)
        params['gas'] = int(1.1 * gas_estimate)
        build_tx = target.build_transaction(params)
        network.tx(self, web3, build_tx, account)
