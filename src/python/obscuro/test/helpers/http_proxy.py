import os
from pysys.constants import PROJECT


class HTTPProxy:

    @classmethod
    def create(cls, test):
        return HTTPProxy(test)

    def __init__(self, test):
        self.test = test
        self.script = os.path.join(PROJECT.root, 'src', 'python', 'scripts', 'http_proxy.py')
        self.stdout = os.path.join(test.output, 'proxy.out')
        self.stderr = os.path.join(test.output, 'proxy.err')
        self.host = '127.0.0.1'
        self.port = test.getNextAvailableTCPPort()

    def run(self, remote_host, remote_port, filename):
        """Run the websocket proxy."""
        self.test.log.info("Running proxy on port %d" % self.port)
        arguments = []
        arguments.extend(['--host', self.host])
        arguments.extend(['--port', '%d' % self.port])
        arguments.extend(['--remote_host', remote_host])
        arguments.extend(['--remote_port', remote_port])
        arguments.extend(['--filename', filename])
        self.test.log.info(arguments)
        self.test.run_python(self.script, self.stdout, self.stderr, arguments)
        return 'http://%s:%d' % (self.host, self.port)

