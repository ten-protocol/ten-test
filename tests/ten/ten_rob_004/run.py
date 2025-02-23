import json, os
from pysys.constants import FAILED
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
        health = self.ten_health()
        if not health['OverallHealth']:
            self.log.info('Network reports not healthy ... dumping output to health.out')
            with open(os.path.join(self.output, 'health.out'), 'w') as file:
                json.dump(health, file, indent=4)
            self.abort(FAILED, outcomeReason='Network is not healthy at start of test')

        # deploy the contract
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT)
        value = storage.contract.functions.retrieve().call()
        self.assertTrue(value == 2, assertMessage='Retrieved value should be 2')

        # sigint stop and restart
        self.run_stop(network, web3, storage, account, value=10, time=10)

        # sigkill stop and restart
        self.run_stop(network, web3, storage, account, value=20, time=0)


    def run_stop(self, network, web3, storage, account, value, time):
        log = DockerHelper.container_logs(self, 'validator-enclave-0')
        self.log.info('Container has previous restarts %d' % count(log, 'Server started.'))

        # stop the container and true to transact
        DockerHelper.container_stop(self, 'validator-enclave-0', time=time)
        self.assertTrue(self.ten_health()['OverallHealth'] == False, assertMessage='Health should be false')
        try:
            network.transact(self, web3, storage.contract.functions.store(value), account, storage.GAS_LIMIT)
            self.addOutcome(FAILED)
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError), assertMessage='ValueError should be thrown')

        # start the container, wait for it to be active and then transact again
        DockerHelper.container_start(self, 'validator-enclave-0')
        self.wait_for_network(timeout=60)
        network.transact(self, web3, storage.contract.functions.store(value), account, storage.GAS_LIMIT)
        value = storage.contract.functions.retrieve().call()
        self.assertTrue(value == value, assertMessage='Retrieved value should be %d' % value)


