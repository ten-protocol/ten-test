import os, requests, json
from ethsys.basetest import EthereumTest


class PySysTest(EthereumTest):

    def execute(self):
        host = '127.0.0.1'
        port = self.getNextAvailableTCPPort()

        # run a background script
        stdout = os.path.join(self.output, 'listener.out')
        stderr = os.path.join(self.output, 'listener.err')
        script = os.path.join(self.input, 'server.js')
        args = []
        args.extend(['--port', '%d' % port])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Listening at http', timeout=10)

        requests.post('http://%s:%d' % (host, port), data='SUBSCRIBE', headers={'Content-Type': 'text/plain'})
        requests.post('http://%s:%d' % (host, port), data='UNSUBSCRIBE', headers={'Content-Type': 'text/plain'})
