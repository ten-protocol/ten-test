import os, requests
from pysys.constants import PROJECT


class AllEventsLogSubscriber:
    """A wrapper over the JS all events log subscribing cli tool. """

    def __init__(self, test, network, contract_address, contract_abi, stdout='subscriber.out', stderr='subscriber.err'):
        """Create an instance of the event log subscriber."""
        self.test = test
        self.network = network
        self.contract_address = contract_address
        self.contract_abi = contract_abi
        self.stdout = os.path.join(test.output, stdout)
        self.stderr = os.path.join(test.output, stderr)
        self.script = os.path.join(PROJECT.root, 'src', 'javascript', 'scripts', 'all_events_subscriber.js')

    def run(self, pk_to_register=None):
        """Run the javascript client event log subscriber. """
        args = []
        args.extend(['--network_ws', self.network.connection_url(web_socket=True)])
        args.extend(['--contract_address', self.contract_address])
        args.extend(['--contract_abi', self.contract_abi])
        if pk_to_register: self.network.connect(self.test, private_key=pk_to_register)
        self.test.run_javascript(self.script, self.stdout, self.stderr, args)
        self.test.waitForGrep(file=self.stdout, expr='Subscription confirmed with id:', timeout=30)


class FilterLogSubscriber:
    """A wrapper over the JS filter log subscribing cli tool. """

    def __init__(self, test, network, stdout='subscriber.out', stderr='subscriber.err'):
        """Create an instance of the event log subscriber."""
        self.test = test
        self.network = network
        self.port = test.getNextAvailableTCPPort()
        self.stdout = os.path.join(test.output, stdout)
        self.stderr = os.path.join(test.output, stderr)
        self.script = os.path.join(PROJECT.root, 'src', 'javascript', 'scripts', 'filter_subscriber.js')

    def run(self, filter_address=None, filter_from_block=None, filter_topics=None, pk_to_register=None,
            network_ws=None, decode_as_stored_event=False):
        """Run the javascript client event log subscriber. """
        if network_ws is None:
            network_ws = self.network.connection_url(web_socket=True)

        args = []
        args.extend(['--script_server_port', '%d' % self.port])
        args.extend(['--network_ws', network_ws])
        if filter_from_block: args.extend(['--filter_from_block', '%d' % filter_from_block])
        if filter_address: args.extend(['--filter_address', filter_address])
        if filter_topics: args.extend(['--filter_topics', " ".join(filter_topics)])
        if decode_as_stored_event: args.append('--decode_as_stored_event')
        if pk_to_register: self.network.connect(self.test, private_key=pk_to_register, check_funds=False)
        self.test.run_javascript(self.script, self.stdout, self.stderr, args)
        self.test.waitForGrep(file=self.stdout, expr='Subscriber listening for instructions', timeout=10)

    def subscribe(self):
        """Request the subscriber to subscribe for logs. """
        requests.post('http://127.0.0.1:%d' % self.port, data='SUBSCRIBE', headers={'Content-Type': 'text/plain'})
        self.test.waitForGrep(file=self.stdout, expr='Subscribed for event logs', timeout=10)

    def unsubscribe(self):
        """Request the subscriber to unsubscribe for logs. """
        requests.post('http://127.0.0.1:%d' % self.port, data='UNSUBSCRIBE', headers={'Content-Type': 'text/plain'})
        self.test.waitForGrep(file=self.stdout, expr='Unsubscribed for event logs', timeout=10)
