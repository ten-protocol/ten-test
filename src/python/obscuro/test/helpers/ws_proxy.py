import os
from pysys.constants import PROJECT


class WebServerProxy:

    @classmethod
    def create(cls, test):
        return WebServerProxy(test)

    def __init__(self, test):
        self.test = test
        self.script = os.path.join(PROJECT.root, 'src', 'python', 'scripts', 'ws_proxy.py')
        self.stdout = os.path.join(test.output, 'proxy.out')
        self.stderr = os.path.join(test.output, 'proxy.err')
        self.host = '127.0.0.1'
        self.port = test.getNextAvailableTCPPort()

    def run(self, remote_url, filename):
        """Run the websocket proxy."""
        self.test.log.info("Running proxy on port %d" % self.port)
        arguments = []
        arguments.extend(['--host', self.host])
        arguments.extend(['--port', '%d' % self.port])
        arguments.extend(['--remote_url', remote_url])
        arguments.extend(['--filename', filename])
        self.test.run_python(self.script, self.stdout, self.stderr, arguments)
        self.test.waitForSignal(self.stdout, expr='Connection bound and listening', timeout=30)
        self.test.waitForSocket(host=self.host, port=self.port, timeout=30)
        return 'ws://%s:%d' % (self.host, self.port)

