import time, math
from pysys.constants import *
from ten.test.utils.docker import DockerHelper
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


def count(filename, search_string):
    try:
        with open(filename, 'r') as file:
            content = file.read()
            count = content.count(search_string)
        return count
    except FileNotFoundError:
        return None


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # check the sequencer is actually reporting itself as healthy
        if self.sequencer_health(dump_to='initial_health.out'): self.log.info('Sequencer reports itself to be healthy')
        else: self.log.warn('Sequencer reports itself to NOT be healthy')

        # deploy the contract
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT, timeout=120)
        value = storage.contract.functions.retrieve().call()
        self.assertTrue(value == 2, assertMessage='Retrieved value should be 2')

        # sigint stop and restart
        self.log.info('')
        self.log.info('Performing SIGINT test')
        self.run_stop(storage, value=10, duration=10, type='sigint')

        # sigkill stop and restart
        self.log.info('')
        self.log.info('Performing SIGKILL test')
        self.run_stop(storage, value=20, duration=0, type='sigkill')

    def run_stop(self, storage, value, duration, type):
        # stop the container, wait for the container to be stopped
        DockerHelper.container_stop(self, 'sequencer-host', time=duration, name=type)
        self.wait_for_stopped()

        # start the container, wait for the sequencer to be healthy then transact
        t1 = int(time.time())
        DockerHelper.container_start(self, 'sequencer-host')
        self.wait_for_sequencer()
        t2 = int(time.time())
        DockerHelper.container_logs(self, 'sequencer-host', state=BACKGROUND, name=type, since='%dm' % math.ceil((t2-t1) / 60))

        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        network.transact(self, web3, storage.contract.functions.store(value), account, storage.GAS_LIMIT, timeout=120)
        value = storage.contract.functions.retrieve().call()
        self.assertTrue(value == value, assertMessage='Retrieved value should be %d' % value)

    def wait_for_stopped(self, timeout=20):
        start = time.time()
        while True:
            time.sleep(1.0)
            if (time.time() - start) > timeout:
                self.addOutcome(TIMEDOUT, 'Timed out waiting %d secs for container to be stopped'%timeout, abortOnError=True)
            if not DockerHelper.container_running(self, 'sequencer-host'):
                self.log.info('Sequencer host is not running after %d secs'%(time.time() - start))
                break
            else: self.log.info('Sequencer host is still running ... waiting')