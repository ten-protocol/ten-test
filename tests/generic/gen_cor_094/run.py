import random, string, os, json
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.emitter import TransparentEventEmitter
from ten.test.helpers.log_subscriber import FilterLogSubscriber


def rstr():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        emitter = TransparentEventEmitter(self, web3)
        emitter.deploy(network, account)

        # run the javascript event log subscriber in the background
        subscriber = FilterLogSubscriber(self, network)
        subscriber.run(
            filter_topics=[web3.keccak(text='StructEvent(uint256,(uint256,string,address))').hex()],
        )
        subscriber.subscribe()

        # transact
        network.transact(self, web3, emitter.contract.functions.emitStructEvent(int(2), rstr()), account, emitter.GAS_LIMIT)

        # wait and validate
        self.waitForGrep(file=subscriber.stdout, expr='Full log:', timeout=20)
        self.assertLineCount(file=subscriber.stdout, expr='Full log:', condition='==1')

