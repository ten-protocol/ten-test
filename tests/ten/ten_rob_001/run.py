from web3 import Web3
import secrets, os
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage
from ten.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(TenNetworkTest):
    NUM_SUBSCRIBERS = 4     # the number of permanent subscribers
    NUM_HAMMERS = 5         # the number of clients which subscribe and then unsubscribe
    NUM_TRANSACTIONS = 15   # how many transactions to perform to test the subscriptions

    def __init__(self, descriptor, outsubdir, runner):
        super().__init__(descriptor, outsubdir, runner)
        self.subscribers = []

    def execute(self):
        # connect to network and deploy contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # the subscribers (permanent for the duration of the test)
        for i in range(0, self.NUM_SUBSCRIBERS): self.subscriber(web3, network, secrets.token_hex(32), i)

        # the hammers (brute force subscribe and unsubscribe)
        for i in range(0, self.NUM_HAMMERS): self.hammer(network, secrets.token_hex(32), i)

        # perform some transactions
        for i in range(0, self.NUM_TRANSACTIONS):
            network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS_LIMIT)

        # all permanent subscribers should see all events - note waitForGrep does not apply a PASSED result if
        # successful (will apply FAILED if timedout), so explicitly do this so the test is verified with a result
        for subscriber in self.subscribers:
            self.waitForGrep(file=subscriber.stdout, expr='Stored value', condition='==%d' % self.NUM_TRANSACTIONS)
            self.assertLineCount(file=subscriber.stdout, expr='Stored value', condition='==%d' % self.NUM_TRANSACTIONS)

    def hammer(self, network, private_key, num):
        # register out-side of the script
        self.distribute_native(Web3().eth.account.from_key(private_key), network.ETH_ALLOC_EPHEMERAL)
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
        self.subscribers.append(subscriber)



