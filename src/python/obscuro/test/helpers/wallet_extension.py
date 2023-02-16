import os
from pysys.constants import PROJECT, BACKGROUND
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.obscuro import Obscuro


class WalletExtension:

    def __init__(self, test, port=None, ws_port=None, name=None):
        """Create an instance of the event log subscriber."""
        self.test = test
        self.port = port if port is not None else test.getNextAvailableTCPPort()
        self.ws_port = ws_port if ws_port is not None else test.getNextAvailableTCPPort()

        if name is None: name = str(port)
        self.logPath = os.path.join(test.output, 'wallet_%s_logs.txt' % name)
        self.persistencePath = os.path.join(test.output, 'wallet_%s_persistence' % name)
        self.stdout = os.path.join(test.output, 'wallet_%s.out' % name)
        self.stderr = os.path.join(test.output, 'wallet_%s.err' % name)
        self.binary = os.path.join(PROJECT.root, 'artifacts', 'wallet_extension', 'wallet_extension')

        if os.path.exists(self.persistencePath):
            test.log.info('Removing wallet extension persistence file')
            os.remove(self.persistencePath)

    def run(self):
        """Run a single wallet extension for use by the tests. """
        self.test .log.info('Starting wallet extension on port=%d, ws_port=%d' % (self.port, self.ws_port))
        props = Properties()

        arguments = []
        arguments.extend(('--nodeHost', props.node_host(self.test)))
        arguments.extend(('--nodePortHTTP', props.node_port_http(self.test.env)))
        arguments.extend(('--nodePortWS', props.node_port_ws(self.test.env)))
        arguments.extend(('--port', str(self.port)))
        arguments.extend(('--portWS', str(self.ws_port)))
        arguments.extend(('--logPath', self.logPath))
        arguments.extend(('--persistencePath', self.persistencePath))
        hprocess = self.test.startProcess(command=self.binary, displayName='wallet_extension',
                                          workingDir=self.test.output, environs=os.environ, quiet=True,
                                          arguments=arguments, stdout=self.stdout, stderr=self.stderr, state=BACKGROUND)
        self.test.waitForSignal(self.stdout, expr='Wallet extension started', timeout=30)
        return hprocess

    def connection_url(self, web_socket=False):
        port = self.port if not web_socket else self.ws_port
        host = Obscuro.HOST if not web_socket else Obscuro.WS_HOST
        return '%s:%d' % (host, port)