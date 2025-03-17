from web3.exceptions import TimeExhausted
from pysys.constants import *
from ten.test.utils import fullname
from pysys.constants import LOG_WARN
from pysys.utils.logutils import BaseLogFormatter
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
        if not self.ten_health(dump_to='health.out'):
            self.abort(FAILED, outcomeReason='Network is not healthy at start of test')

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
        log = DockerHelper.container_logs(self, 'sequencer-enclave-0')
        self.log.info('Container has previous restarts %d' % count(log, 'Server started.'))

        # stop the container and true to transact
        DockerHelper.container_stop(self, 'sequencer-enclave-0', time=time)
        self.assertTrue(not self.ten_health(), assertMessage='Health should be false')
        try:
            target = storage.contract.functions.store(value)
            self.log.info('Account %s performing transaction %s', account.address, fullname(target), extra=BaseLogFormatter.tag(LOG_WARN, 1))
            nonce = network.get_next_nonce(self, web3, account.address, False)
            tx = network.build_transaction(self, web3, target, nonce, account.address, storage.GAS_LIMIT)
            tx_sign = network.sign_transaction(self, tx, nonce, account, False)
            tx_hash = network.send_transaction(self, web3, nonce, account.address, tx_sign, False)
            tx_recp = network.wait_for_transaction(self, web3, nonce, account.address, tx_hash, False)
            self.addOutcome(FAILED)
        except TimeExhausted as e:
            self.log.warn('Exception: %s' % e)
            self.assertTrue(isinstance(e, ValueError), assertMessage='TimeExhausted should be thrown')

            self.addOutcome(FAILED)
        except Exception as e:
            self.log.warn('Exception: %s' % e)
            self.assertTrue(isinstance(e, ValueError), assertMessage='ValueError should be thrown')

        # start the container, wait for it to be active and then transact again
        DockerHelper.container_start(self, 'sequencer-enclave-0')
        self.wait_for_network(timeout=60)
        network.transact(self, web3, storage.contract.functions.store(value), account, storage.GAS_LIMIT)
        value = storage.contract.functions.retrieve().call()
        self.assertTrue(value == value, assertMessage='Retrieved value should be %d' % value)
