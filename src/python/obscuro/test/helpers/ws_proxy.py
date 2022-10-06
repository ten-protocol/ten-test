import os
from pysys.constants import PROJECT


class WebServerProxy():

    def run_ws_proxy(self, test, remote_url, filename):
        """Run the websocket proxy to log messages."""
        script = os.path.join(PROJECT.root, 'utils', 'proxy', 'ws_proxy.py')
        stdout = os.path.join(test.output, 'proxy.out')
        stderr = os.path.join(test.output, 'proxy.err')

        host = '127.0.0.1'
        port = test.getNextAvailableTCPPort()
        arguments = []
        arguments.extend(['--host', host])
        arguments.extend(['--port', '%d' % port])
        arguments.extend(['--remote_url', remote_url])
        arguments.extend(['--filename', filename])
        test.run_python(script, stdout, stderr, arguments)
        return 'ws://%s:%d' % (host, port)