from web3 import Web3
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.relevancy import Relevancy
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account4(self)
        account1 = Web3().eth.account.privateKeyToAccount(Properties().account1pk())

        # deploy the storage contract
        contract = Relevancy(self, web3)
        contract.deploy(network, account)

        # run the javascript event log subscriber in the background for the other accounts
        self.subscribe(network, None, 'account4', contract.address, contract.abi_path)
        self.subscribe(network, Properties().account1pk(), 'account1', contract.address, contract.abi_path, new_wallet=True)
        self.subscribe(network, Properties().account2pk(), 'account2', contract.address, contract.abi_path, new_wallet=True)
        self.subscribe(network, Properties().account3pk(), 'account3', contract.address, contract.abi_path, new_wallet=True)
        self.wait(float(self.block_time) * 1.1)

        # perform some transactions
        self.log.info('Performing transactions ... ')
        network.transact(self, web3,
                         contract.contract.functions.twoIndexedAddresses(account.address, account1.address),
                         account, contract.GAS_LIMIT)
        self.wait(float(self.block_time)*1.1)

        # wait and assert that account4 does see this event
        self.waitForGrep(file='subscriber_account4.out', expr='Received event: TwoIndexedAddresses', timeout=20)
        self.assertGrep(file='subscriber_account4.out', expr='Received event: TwoIndexedAddresses')

        # wait and assert that account1 does see this event
        self.waitForGrep(file='subscriber_account1.out', expr='Received event: TwoIndexedAddresses', timeout=20)
        self.assertGrep(file='subscriber_account1.out', expr='Received event: TwoIndexedAddresses')

        # assert that the other two users do not see the event
        self.assertGrep(file='subscriber_account2.out', expr='Received event: TwoIndexedAddresses', contains=False)
        self.assertGrep(file='subscriber_account3.out', expr='Received event: TwoIndexedAddresses', contains=False)

    def subscribe(self, network, pk_to_register, name, address, abi_path, new_wallet=False):
        if new_wallet:
            network = self.get_network_connection(name=name)

        subscriber = AllEventsLogSubscriber(self, network, address, abi_path,
                                            stdout='subscriber_%s.out' % name,
                                            stderr='subscriber_%s.err' % name)
        subscriber.run(pk_to_register)

