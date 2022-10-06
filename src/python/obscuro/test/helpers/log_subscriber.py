import os, requests
from pysys.constants import PROJECT


class EventLogSubscriber:

    def __init__(self, test, network, stdout='subscriber.out', stderr='subscriber.err'):
        """Create an instance of the event log subscriber."""
        self.test = test
        self.network = network
        self.port = test.getNextAvailableTCPPort()
        self.stdout = os.path.join(test.output, stdout)
        self.stderr = os.path.join(test.output, stderr)
        self.script = os.path.join(PROJECT.root, 'src', 'javascript', 'scripts', 'logs', 'subscriber.js')

    def run(self, filter_address=None, filter_from_block=None, filter_topics=None, pk_to_register=None):
        """Run a javascript client event log subscriber. """
        args = []
        args.extend(['--script_server_port', '%d' % self.port])
        args.extend(['--network_http', '%s' % self.network.connection_url(web_socket=False)])
        args.extend(['--network_ws', '%s' % self.network.connection_url(web_socket=True)])
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
