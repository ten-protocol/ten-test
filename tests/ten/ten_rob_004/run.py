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

        # check the validator is actually reporting itself as healthy
        if self.validator_health(dump_to='health.out'): self.log.info('Validator reports itself to be healthy')
        else: self.log.warn('Validator reports itself to NOT be healthy')

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
        stdout, _ = DockerHelper.container_logs(self, 'validator-enclave-0')
        self.log.info('Container has previous restarts %d' % count(stdout, 'Server started.'))

        # stop the container, wait for it to be stopped then try to transact
        DockerHelper.container_stop(self, 'validator-enclave-0', time=time)
        self.wait_for_stopped()
        self.assertTrue(not self.validator_health(), assertMessage='Health should be false')
        try:
            network.transact(self, web3, storage.contract.functions.store(value), account, storage.GAS_LIMIT)
            self.addOutcome(FAILED)
        except Exception as e:
            self.log.warn('Exception: %s' % e)
            self.assertTrue(isinstance(e, ValueError), assertMessage='ValueError should be thrown')

        # start the container, wait for it to be active and then transact again
        DockerHelper.container_start(self, 'validator-enclave-0')
        self.wait_for_validator()
        network.transact(self, web3, storage.contract.functions.store(value), account, storage.GAS_LIMIT)
        value = storage.contract.functions.retrieve().call()
        self.assertTrue(value == value, assertMessage='Retrieved value should be %d' % value)

    def wait_for_stopped(self, timeout=20):
        start = time.time()
        while True:
            time.sleep(1.0)
            if (time.time() - start) > timeout:
                self.addOutcome(TIMEDOUT, 'Timed out waiting %d secs for container to be stopped'%timeout, abortOnError=True)
            if not DockerHelper.container_running(self, 'validator-enclave-0'):
                self.log.info('Validator enclave is not running after %d secs'%(time.time() - start))
                break
            else: self.log.info('Validator enclave is still running ... waiting')
