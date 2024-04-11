import json, os
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        # get a token from the gateway
        token = self.gateway_get_token()
        self.log.info('Token is: %s', token)

        self.log.info('Running for EIP712')
        message = json.loads(self.gateway_get_message(token=token, formats=["EIP712"]))["message"]
        with open(os.path.join(self.output, 'msg_eip712.json'), 'w') as f:
            json.dump(message, f, indent=4)

        self.log.info('Running for Personal')
        message = json.loads(self.gateway_get_message(token=token, formats=["Personal"]))["message"]
        with open(os.path.join(self.output, 'msg_personal.json'), 'w') as f:
            json.dump(message, f, indent=4)

        self.log.info('Running for both')
        message = json.loads(self.gateway_get_message(token=token, formats=["EIP712","Personal"]))["message"]
        with open(os.path.join(self.output, 'msg_both.json'), 'w') as f:
            json.dump(message, f, indent=4)

        self.log.info('Asserting diff against reference files')
        self.assertDiff(file1='msg_eip712.json', file2='msg_eip712.json', replace=[('<token>', token)])
        self.assertDiff(file1='msg_personal.json', file2='msg_personal.json', replace=[('<token>', token)])
        self.assertDiff(file1='msg_both.json', file2='msg_both.json', replace=[('<token>', token)])
