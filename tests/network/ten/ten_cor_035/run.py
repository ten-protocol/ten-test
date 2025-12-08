import requests
from pysys.constants import FAILED, PASSED
from ten.test.utils.properties import Properties
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def gateway_network_config(self):
        props = Properties()
        url = '%s:%d/v1/network-config/' % (props.host_http(self.env), props.port_http(self.env))
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.get(url, headers=headers)
        return url, response

    def execute(self):
        # get the network config from the available url and log out the valaues
        url, response = self.gateway_network_config()
        self.log.info('Headers return in the url are;')
        for k,v in response.headers.items():
            self.log.info('  %s: %s', k, v)

        expected = {}
        expected['Content-Security-Policy'] = 'frame-ancestors \'none\''
        expected['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=(), payment=(), usb=(), accelerometer=(), gyroscope=(), magnetometer=(), fullscreen=(), autoplay=()'
        expected['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        expected['X-Content-Type-Options'] = 'nosniff'
        expected['X-Frame-Options'] = 'DENY'
        if url.startswith('https:'): expected['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        for k,v in expected.items():
            if not k in response.headers.keys():
                self.addOutcome(FAILED, outcomeReason='%s should be in the header'%k)
            else:
                if response.headers[k] != v:
                    self.addOutcome(FAILED, outcomeReason='value of %s should match expected'%v)
                else:
                    self.addOutcome(PASSED, outcomeReason='%s value is as expected'%k)

