import os
from pysys.constants import PROJECT, BACKGROUND
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.obscuro import Obscuro


class WalletExtension:
    """A wrapper over the Obscuro wallet extension. """

    @classmethod
    def start(cls, parent, port=None, ws_port=None, name=None, verbose=True):
        extension = WalletExtension(parent, port, ws_port, name, verbose)
        extension.run()
        return extension

    def __init__(self, test, port=None, ws_port=None, name=None, verbose=True,
                 node_host=None, node_port_http=None, node_port_ws=None):
        """Create an instance of the wrapper. """
        self.test = test
        self.port = port if port is not None else test.getNextAvailableTCPPort()
        self.ws_port = ws_port if ws_port is not None else test.getNextAvailableTCPPort()
        self.verbose = verbose

        props = Properties()
        self.node_host = node_host if node_host is not None else props.node_host(test.env,test.NODE_HOST)
        self.node_port_http = node_port_http if node_port_http is not None else props.node_port_http(self.test.env)
        self.node_port_ws = node_port_ws if node_port_ws is not None else props.node_port_ws(self.test.env)

        if name is None: name = str(port)
        self.logPath = os.path.join(test.output, 'wallet_%s_logs.txt' % name)
        self.databasePath = os.path.join(test.output, 'wallet_%s_database' % name)
        self.stdout = os.path.join(test.output, 'wallet_%s.out' % name)
        self.stderr = os.path.join(test.output, 'wallet_%s.err' % name)
        self.binary = os.path.join(PROJECT.root, 'artifacts', 'wallet_extension', 'wallet_extension')

        if os.path.exists(self.databasePath):
            test.log.info('Removing wallet extension persistence file')
            os.remove(self.databasePath)

    def run(self):
        """Run an instance of the wallet extension. """
        self.test.log.info('Starting wallet extension on port=%d, ws_port=%d', self.port, self.ws_port)
        props = Properties()

        arguments = []
        arguments.extend(('--nodeHost', self.node_host))
        arguments.extend(('--nodePortHTTP', self.node_port_http))
        arguments.extend(('--nodePortWS', self.node_port_ws))
        arguments.extend(('--port', str(self.port)))
        arguments.extend(('--portWS', str(self.ws_port)))
        arguments.extend(('--logPath', self.logPath))
        arguments.extend(('--databasePath', self.databasePath))
        if self.verbose: arguments.append('--verbose')
        hprocess = self.test.startProcess(command=self.binary, displayName='wallet_extension',
                                          workingDir=self.test.output, environs=os.environ, quiet=True,
                                          arguments=arguments, stdout=self.stdout, stderr=self.stderr, state=BACKGROUND)
        self.test.waitForSignal(self.stdout, expr='Wallet extension started', timeout=30)
        return hprocess

    def connection_url(self, web_socket=False):
        """Return the connection URL to the wallet extension. """
        port = self.port if not web_socket else self.ws_port
        host = Obscuro.HOST if not web_socket else Obscuro.WS_HOST
        return '%s:%d' % (host, port)