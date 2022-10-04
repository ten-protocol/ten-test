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

        data = {"command": 'subscribe'}
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.post('http://%s:%d' % (host, port), data=json.dumps(data), headers=headers)
