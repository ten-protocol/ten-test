import requests
from pysys.constants import FAILED, PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.helpers.wallet_extension import WalletExtension


class PySysTest(TenNetworkTest):

    def execute(self):
        wallet = WalletExtension(self, name='local')
        wallet.run(httpRateLimitPerIPRate=10)
        for i in range(0,25): self.join(port=wallet.port, expect_fail=(i>=15))
        self.wait(2.0)
        for i in range(0,25): self.join(port=wallet.port, expect_fail=(i>=15))

    def join(self, port, host='http://127.0.0.1', expect_fail=False):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.get('%s:%d/v1/join/' % (host, port),  headers=headers)
        if response.ok:
            if expect_fail: self.addOutcome(FAILED, 'Expected fail due to rate limiting')
            else: self.addOutcome(PASSED, 'Joined as expected with token %s' % response.text)
        else:
            if expect_fail: self.addOutcome(PASSED, 'Expected fail due to rate limiting: %s' % response.json()['error'])
            else: self.addOutcome(FAILED, 'Expected pass due to rate limiting')


