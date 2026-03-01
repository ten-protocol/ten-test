import requests
from pysys.constants import FAILED, PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.helpers.gateway import Gateway


class PySysTest(TenNetworkTest):

    def execute(self):
        self.log.info(' ')
        self.log.info('Running against gw with no rate limiting on the join')
        gateway = Gateway(self, name='local_no_limit')
        gateway.run()
        for i in range(0, 20): self.join(port=gateway.port, expect_fail=False)

        self.log.info(' ')
        self.log.info('Running against gw with rate limiting on the join')
        gateway = Gateway(self, name='local_with_limit')
        gateway.run(httpRateLimitGlobalRate=10)
        for i in range(0, 20): self.join(port=gateway.port, expect_fail=(i >= 15))
        self.wait(2.0)
        for i in range(0, 20): self.join(port=gateway.port, expect_fail=(i >= 15))

    def join(self, port, host='http://127.0.0.1', expect_fail=False):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.get('%s:%d/v1/join/' % (host, port), headers=headers)
        if response.ok:
            if expect_fail: self.addOutcome(FAILED, 'Expected fail due to rate limiting')
            else: self.addOutcome(PASSED, 'Joined as expected with token %s' % response.text)
        else:
            if expect_fail: self.addOutcome(PASSED, 'Expected fail due to rate limiting: %s' % response.json()['error'])
            else: self.addOutcome(FAILED, 'Expected pass due to rate limiting')
