import os
from pysys.constants import PROJECT


class HTTPProxy:
    """A wrapper of the python HTTP proxy to log messages communications.

    Note the HTTP proxy is still a work in progress. Should you want to use a proxy it is currently
    recommended to use the WebSocketProxy instead. """

    @classmethod
    def create(cls, test):
        """Class method to create and return an instance of the proxy. """
        return HTTPProxy(test)

    def __init__(self, test):
        """Instantiate an instance of the proxy. """
        self.test = test
        self.script = os.path.join(PROJECT.root, 'src', 'python', 'scripts', 'http_proxy.py')
        self.stdout = os.path.join(test.output, 'http_proxy.out')
        self.stderr = os.path.join(test.output, 'http_proxy.err')
        self.port = test.getNextAvailableTCPPort()

    def run(self, remote_host, remote_port, filename):
        """Run the http proxy."""
        self.test.log.info("Running proxy on port %d", self.port)
        arguments = []
        arguments.extend(['--port', '%d' % self.port])
        arguments.extend(['--remote_host', remote_host])
        arguments.extend(['--remote_port', '%d' % remote_port])
        arguments.extend(['--filename', filename])
        self.test.run_python(self.script, self.stdout, self.stderr, arguments)
        self.test.waitForSignal(self.stdout, expr='Connection bound and listening', timeout=30)
        return 'http://127.0.0.1:%d' % self.port

