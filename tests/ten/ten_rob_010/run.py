import os, secrets
from web3 import Web3
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):
    NUM_CLIENTS = 10           # the number of concurrent clients
    NUM_ITERATIONS = 25        # the number of times to loop through joining and registering
    ADDITIONAL_ACCOUNTS = 8    # how many additional accounts to do for each iteration
    FUNDS = 10                 # the funds amount to give them (can be low so in wei)

    def execute(self):
        # connect to the network on the primary gateway
        network = self.get_network_connection()
        trigger = os.path.join(self.output, '.trigger')

        self.log.info('Creating the clients')
        for i in range(0, self.NUM_CLIENTS):
            self._client('client_%s' % i, network, trigger)

        self.log.info('Starting the clients using trigger')
        with open(trigger, 'w') as fp:
            fp.write('Good to go chaps!')
            fp.flush()

        self.log.info('Waiting for the clients to complete')
        for i in range(0, self.NUM_CLIENTS):
            self.waitForGrep(file=os.path.join(self.output, 'client_%s.out' % i), expr='Client completed', timeout=120)

        self.log.info('Confirm balances were received for all interactions')
        for i in range(0, self.NUM_CLIENTS):
            self.assertLineCount(file=os.path.join(self.output, 'client_%s.out' % i),
                                 expr='Balance is %d' % self.FUNDS, condition='== %d' % self.NUM_ITERATIONS)

    def _client(self, name, network, trigger):
        pk = secrets.token_hex(32)
        account = Web3().eth.account.from_key(pk)
        self.distribute_native(account, Web3().from_wei(self.FUNDS, 'ether'))

        stdout = os.path.join(self.output, '%s.out' % name)
        stderr = os.path.join(self.output, '%s.err' % name)
        script = os.path.join(self.input, 'connector.py')
        args = []
        args.extend(['--host', '%s' % network.HOST])
        args.extend(['--port', '%d' % network.PORT])
        args.extend(['--pk', '%s' % pk])
        args.extend(['--balance', '0.01'])
        args.extend(['--trigger', trigger])
        args.extend(['--iterations', '%s' % self.NUM_ITERATIONS])
        args.extend(['--additional_accounts', '%s' % self.ADDITIONAL_ACCOUNTS])
        args.extend(['--chain_id', '%s' % Properties().chain_id(self.env)])
        self.run_python(script, stdout, stderr, args)