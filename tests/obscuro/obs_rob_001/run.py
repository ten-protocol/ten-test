from web3 import Web3
import secrets, os
from pysys.constants import PASSED
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage import Storage
from obscuro.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(GenericNetworkTest):
    NUM_SUBSCRIBERS=4
    NUM_HAMMERS=5
    NUM_TRANSACTIONS=15

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # the subscribers
        for i in range(0, self.NUM_SUBSCRIBERS):  self.subscriber(web3, network, secrets.token_hex(32), i)

        # the hammers (brute force subscribe and unsubscribe)
        for i in range(0, self.NUM_HAMMERS): self.hammer(network, secrets.token_hex(32), i)

        # perform some transactions
        for i in range(0, self.NUM_TRANSACTIONS):
            network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS_LIMIT)

        # if we get this far we've passed
        self.addOutcome(PASSED)

    def hammer(self, network, private_key, num):
        # register out-side of the script
        self.distribute_native(Web3().eth.account.privateKeyToAccount(private_key), 0.01)
        network.connect(self, private_key=private_key, check_funds=False)

        # create the client
        stdout = os.path.join(self.output, 'hammer_%d.out'%num)
        stderr = os.path.join(self.output, 'hammer_%d.err'%num)
        script = os.path.join(self.input, 'hammer.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Subscribing for event logs', timeout=10)

    def subscriber(self, web3, network, private_key, num):
        subscriber = FilterLogSubscriber(self, network, stdout='subscriber_%d.out'%num, stderr='subscriber_%d.err'%num)
        subscriber.run(
            decode_as_stored_event=True,
            pk_to_register=private_key,
            filter_topics=[web3.keccak(text='Stored(uint256)').hex()]
        )
        subscriber.subscribe()



