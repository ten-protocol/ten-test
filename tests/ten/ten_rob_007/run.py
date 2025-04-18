import time
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

        # check the network is actually reporting itself as healthy
        if self.ten_health(dump_to='health.out'): self.log.info('Network reports itself to be healthy')
        else: self.log.warn('Network reports itself to NOT be healthy')

        # deploy the contract
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT)
        value = storage.contract.functions.retrieve().call()
        self.assertTrue(value == 2, assertMessage='Retrieved value should be 2')

        # sigint stop and restart
        self.log.info('')
        self.log.info('Performing SIGINT test')
        self.run_stop(network, web3, storage, account, value=10, time=10)

        # sigkill stop and restart
        self.log.info('')
        self.log.info('Performing SIGKILL test')
        self.run_stop(network, web3, storage, account, value=20, time=0)

    def run_stop(self, network, web3, storage, account, value, time):
        stdout, stderr = DockerHelper.container_logs(self, 'sequencer-host')
        restarts = count(stdout, 'Server started')
        self.log.info('Container has previous restarts %d' % restarts)

        # stop the container
        DockerHelper.container_stop(self, 'sequencer-host', time=time)
        self.wait_for_stopped()

        # start the container, wait for it to be active and then transact
        DockerHelper.container_start(self, 'sequencer-host')
        self.wait_for_started(restarts)

        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        network.transact(self, web3, storage.contract.functions.store(value), account, storage.GAS_LIMIT, timeout=30)
        value = storage.contract.functions.retrieve().call()
        self.assertTrue(value == value, assertMessage='Retrieved value should be %d' % value)

    def wait_for_started(self, restarts, timeout=120):
        self.log.info('Waiting for server to restart ...')
        start = time.time()
        while True:
            if (time.time() - start) > timeout:
                self.addOutcome(TIMEDOUT, 'Timed out waiting %d secs for network to be healthy'%timeout, abortOnError=True)
            stdout, stderr = DockerHelper.container_logs(self, 'sequencer-host')
            _num_restarts = count(stdout, 'Server started')
            if _num_restarts >= restarts+1:
                self.log.info('Server is running after %d secs'%(time.time() - start))
                break
            else: self.log.info('Server has not yet restarted ... waiting')
            time.sleep(3.0)

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