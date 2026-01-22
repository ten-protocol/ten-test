import requests
from ten.test.basetest import TenNetworkTest
from ten.test.helpers.wallet_extension import WalletExtension


class PySysTest(TenNetworkTest):

    def execute(self):
        wallet = WalletExtension(self, name='local')
        wallet.run(httpRateLimitPerIPRate=10)
        for i in range(0,25): self.join(port=wallet.port)

    def join(self, port, host='http://127.0.0.1'):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.get('%s:%d/v1/join/' % (host, port),  headers=headers)
        if response.ok:
            self.log.info(response.text.strip())
        else:
            self.log.info(response)


