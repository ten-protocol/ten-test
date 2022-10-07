import os, time, shutil, sys
from pysys.constants import PROJECT, BACKGROUND
from pysys.exceptions import AbortExecution
from obscuro.test.networks.ganache import Ganache
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.utils.properties import Properties


class ObscuroRunnerPlugin():
    """Runner class for running a set of tests against a given environment.

    The runner is responsible for starting any applications up prior to running the requested tests. When running
    against Ganache, a local Ganache will be started; when running against Obscuro, the Obscuro wallet extension
    will be started. All processes started by the runner are automatically stopped when the tests are complete.
    """

    def setup(self, runner):
        """Set up a runner plugin to start any processes required to execute the tests."""
        self.env = 'obscuro' if runner.mode is None else runner.mode
        runner.log.info('Runner is executing against environment %s' % self.env)

        self.output = os.path.join(PROJECT.root, '.runner')
        if os.path.exists(self.output): shutil.rmtree(self.output)
        os.makedirs(self.output)

        try:
            if self.is_obscuro():
                self.run_wallets(runner)
            elif self.env == 'ganache':
                self.run_ganache(runner)
        except AbortExecution as e:
            runner.log.info('Error executing runner plugin startup actions', e)
            runner.log.info('See contents of the .runner directory in the project root for any process output')
            runner.log.info('Exiting ...')
            runner.cleanup()
            sys.exit()

    def is_obscuro(self):
        """Return true if we are running against an Obscuro network. """
        return self.env in ['obscuro', 'obscuro.dev', 'obscuro.local', 'obscuro.sim']

    def run_ganache(self, runner):
        """Run ganache for use by the tests. """
        stdout = os.path.join(self.output, 'ganache.out')
        stderr = os.path.join(self.output, 'ganache.err')

        arguments = []
        arguments.extend(('--port', str(Ganache.PORT)))
        arguments.extend(('--account', '0x%s,1000000000000000000' % Properties().account1pk()))
        arguments.extend(('--account', '0x%s,1000000000000000000' % Properties().account2pk()))
        arguments.extend(('--account', '0x%s,1000000000000000000' % Properties().account3pk()))
        arguments.extend(('--gasLimit', '7200000'))
        arguments.extend(('--blockTime', '1'))
        hprocess = runner.startProcess(command=Properties().ganache_binary(), displayName='ganache',
                                       workingDir=self.output , environs=os.environ, quiet=True,
                                       arguments=arguments, stdout=stdout, stderr=stderr, state=BACKGROUND)

        runner.waitForSignal(stdout, expr='Listening on 127.0.0.1:%d' % Ganache.PORT, timeout=30)
        runner.addCleanupFunction(lambda: self.__stop_process(hprocess))

    def run_wallets(self, runner):
        """Run the wallet extension(s) for use by the tests. """
        home = os.path.expanduser('~')
        persistence_file = os.path.join(home, '.obscuro', 'wallet_extension_persistence')
        if os.path.exists(persistence_file):
            runner.log.info('Removing wallet extension persistence file')
            os.remove(persistence_file)

        self.run_wallet(runner, Obscuro.PORT, Obscuro.WS_PORT)
        time.sleep(1)

    def run_wallet(self, runner, port, ws_port):
        """Run a single wallet extension for use by the tests. """
        runner.log.info('Starting wallet extension on port=%d, ws_port=%d' % (port, ws_port))
        stdout = os.path.join(self.output, 'wallet_%d.out' % port)
        stderr = os.path.join(self.output, 'wallet_%d.err' % port)
        props = Properties()

        arguments = []
        arguments.extend(('--nodeHost', props.node_host(self.env)))
        arguments.extend(('--nodePortHTTP', props.node_port_http(self.env)))
        arguments.extend(('--nodePortWS', props.node_port_ws(self.env)))
        arguments.extend(('--port', str(port)))
        arguments.extend(('--portWS', str(ws_port)))
        arguments.extend(('--logPath', os.path.join(self.output, 'wallet_%d_logs.txt' % port)))
        hprocess = runner.startProcess(command=os.path.join(PROJECT.root, 'artifacts', 'wallet_extension'),
                                       displayName='wallet_extension', workingDir=self.output , environs=os.environ,
                                       quiet=True, arguments=arguments, stdout=stdout, stderr=stderr, state=BACKGROUND)
        runner.waitForSignal(stdout, expr='Wallet extension started', timeout=30)
        runner.addCleanupFunction(lambda: self.__stop_process(hprocess))

    def __stop_process(self, hprocess):
        """Stop a process started by this runner plugin."""
        hprocess.stop()