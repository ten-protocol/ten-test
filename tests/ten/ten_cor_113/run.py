from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.storage import Storage, StorageTwoPhaseWithEvents
from ten.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the storage and storage contract with two phase commit
        storage_two_phase = StorageTwoPhaseWithEvents(self, web3, 100, Properties().L2PublicCallbacks)
        storage_two_phase.deploy(network, account)
        storage_normal = Storage(self, web3, 100)
        storage_normal.deploy(network, account)

        # run the javascript event log subscriber in the background
        subscriber = FilterLogSubscriber(self, network)
        subscriber.run(
            filter_topics=[web3.keccak(text='Stored(uint256)').hex()],
            decode_as_stored_event=True
        )
        subscriber.subscribe()

        # perform some transactions on both contracts
        for i in range(0, 5): self.transact(storage_two_phase, web3, network, account, i)
        network.transact(self, web3, storage_normal.contract.functions.store(21), account, storage_normal.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate
        self.waitForGrep(file=subscriber.stdout, expr='Stored value = 21', timeout=20)
        expr_list = []
        expr_list.append('Stored value = 0')
        expr_list.append('Stored value = 1')
        expr_list.append('Stored value = 2')
        expr_list.append('Stored value = 3')
        expr_list.append('Stored value = 4')
        expr_list.append('Stored value = 21')
        self.assertOrderedGrep(file=subscriber.stdout, exprList=expr_list)
        self.assertLineCount(file=subscriber.stdout, expr='Stored value', condition='== 6')

    def transact(self, storage, web3, network, account, num):
        target = storage.contract.functions.store(num)
        params = {'gasPrice': web3.eth.gas_price, 'value': web3.to_wei(0.01, 'ether')}
        gas_estimate = target.estimate_gas(params)
        params['gas'] = int(1.1 * gas_estimate)
        build_tx = target.build_transaction(params)
        network.tx(self, web3, build_tx, account)
