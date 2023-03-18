import os, requests
from pysys.constants import PROJECT
from obscuro.test.helpers.ws_proxy import WebServerProxy


class AllEventsLogSubscriber:
    """A wrapper over the JS all events log subscribing cli tool. """

    def __init__(self, test, network, contract, stdout='subscriber.out', stderr='subscriber.err'):
        """Create an instance of the event log subscriber."""
        self.test = test
        self.network = network
        self.contract = contract
        self.stdout = os.path.join(test.output, stdout)
        self.stderr = os.path.join(test.output, stderr)
        self.script = os.path.join(PROJECT.root, 'src', 'javascript', 'scripts', 'all_events_subscriber.js')

    def run(self, pk_to_register=None, network_http=None, network_ws=None):
        """Run the javascript client event log subscriber. """
        args = []
        args.extend(['--network_http', network_http])
        args.extend(['--network_ws', network_ws])
        args.extend(['--address', self.contract.address])
        args.extend(['--contract_abi', self.contract.abi_path])
        args.extend(['--pk_to_register', pk_to_register])
        self.test.run_javascript(self.script, self.stdout, self.stderr, args)
        self.test.waitForGrep(file=self.stdout, expr='Subscription confirmed with id:', timeout=10)


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
            network_http=None, network_ws=None):
        """Run the javascript client event log subscriber. """
        if network_ws is None:
            network_ws = self.network.connection_url(web_socket=True)
            if self.test.PROXY: network_ws = WebServerProxy.create(self.test).run(network_ws, 'proxy.logs')

        if network_http is None:
            network_http = self.network.connection_url(web_socket=False)

        args = []
        args.extend(['--script_server_port', '%d' % self.port])
        args.extend(['--network_http', '%s' % network_http])
        args.extend(['--network_ws', network_ws])
        if filter_from_block: args.extend(['--filter_from_block', '%d' % filter_from_block])
        if filter_address: args.extend(['--filter_address', filter_address])
        if filter_topics:args.extend(['--filter_topics', " ".join(filter_topics)])
        if pk_to_register: args.extend(['--pk_to_register', '%s' % pk_to_register])
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
