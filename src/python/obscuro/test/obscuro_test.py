import os, copy, sys
from pysys.basetest import BaseTest
from pysys.constants import PROJECT, BACKGROUND
from obscuro.test.utils.properties import Properties
from obscuro.test.helpers.wallet_extension import WalletExtension
from obscuro.test.networks.obscuro import Obscuro


class ObscuroTest(BaseTest):
    """The base test used by all tests cases, against any request environment.

    The ObscuroTest class provides common utilities used by all tests, which at the moment are the ability to
    start processes outside of the framework to interact with the network, e.g. written in python or javascript. The
    WEBSOCKET and PROXY values can be set at run time using the -X<ATTRIBUTE> option to the pysys run launcher, and
    respectively force all connections to be over websockets, or for a proxy to set inbetween the client and network
    where a test supports these.

    """
    WEBSOCKET = False   # run with `pysys.py run -XWEBSOCKET` to enable
    PROXY = False       # run with `pysys.py run -XPROXY` to enable

    def __init__(self, descriptor, outsubdir, runner):
        """Call the parent constructor but set the mode to obscuro if non is set. """
        super().__init__(descriptor, outsubdir, runner)
        self.env = 'obscuro' if self.mode is None else self.mode

        # every test runs a default wallet extension
        if self.is_obscuro(): self.run_wallet(Obscuro.PORT, Obscuro.WS_PORT)

    def is_obscuro(self):
        """Return true if we are running against an Obscuro network. """
        return self.env in ['obscuro', 'obscuro.dev', 'obscuro.local', 'obscuro.sim']

    def is_obscuro_sim(self):
        """Return true if we are running against an Obscuro simulation network. """
        return self.env in ['obscuro.sim']

    def run_wallet(self, port, ws_port):
        """Run a single wallet extension for use by the tests. """
        extension = WalletExtension(self, port, ws_port)
        return extension.run()

    def run_python(self, script, stdout, stderr, args=None, state=BACKGROUND, timeout=120):
        """Run a python process."""
        self.log.info('Running python script %s' % os.path.basename(script))
        arguments = [script]
        if args is not None: arguments.extend(args)

        environ = copy.deepcopy(os.environ)
        hprocess = self.startProcess(command=sys.executable, displayName='python', workingDir=self.output,
                                     arguments=arguments, environs=environ, stdout=stdout, stderr=stderr,
                                     state=state, timeout=timeout)
        return hprocess

    def run_javascript(self, script, stdout, stderr, args=None, state=BACKGROUND, timeout=120):
        """Run a javascript process."""
        self.log.info('Running javascript %s' % os.path.basename(script))
        arguments = [script]
        if args is not None: arguments.extend(args)

        environ = copy.deepcopy(os.environ)
        node_path = os.path.join(PROJECT.root, 'src', 'javascript', 'modules')
        if "NODE_PATH" in environ:
            environ["NODE_PATH"] = environ["NODE_PATH"] + ":" + node_path
        else:
            environ["NODE_PATH"] = node_path
        hprocess = self.startProcess(command=Properties().node_binary(), displayName='node', workingDir=self.output,
                                     arguments=arguments, environs=environ, stdout=stdout, stderr=stderr,
                                     state=state, timeout=timeout)
        return hprocess


