import os, secrets
from web3 import Web3
from ten.test.basetest import ObscuroNetworkTest


class PySysTest(ObscuroNetworkTest):
    NUM_CLIENTS = 10
    NUM_ITERATIONS = 100
    ADDITIONAL_ACCOUNTS = 8

    def execute(self):
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
            self.waitForGrep(file=os.path.join(self.output, 'client_%s.out' % i), expr='Client completed', timeout=60)

        self.log.info('Confirmation balances were received for all iteractions')
        for i in range(0, self.NUM_CLIENTS):
            self.assertLineCount(file=os.path.join(self.output, 'client_%s.out' % i),
                                 expr='Balance is 10000000000000000', condition='== %d' % self.NUM_ITERATIONS)

    def _client(self, name, network, trigger):
        pk = secrets.token_hex(32)
        account = Web3().eth.account.privateKeyToAccount(pk)
        self.distribute_native(account, 0.01)

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
        self.run_python(script, stdout, stderr, args)