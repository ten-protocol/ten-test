import json, os, requests
from ten.test.utils.properties import Properties
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def gateway_get_token(self):
        props = Properties()
        url = '%s:%d/v1/join/' % (props.host_http(self.env), props.port_http(self.env))
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.get(url, headers=headers)
        return response.text

    def gateway_get_message(self, token, formats=None):
        props = Properties()
        url = '%s:%d/v1/getmessage/' % (props.host_http(self.env), props.port_http(self.env))
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        data = {"encryptionToken": token, "formats": ["EIP712", "Personal"] if formats is None else formats}
        response = requests.get(url, headers=headers, json=data)
        return response.text

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
        replaceList = [('<token>', token)]
        replaceList.append(('<chain_id_hex>', hex(Properties().chain_id(self.env))))
        replaceList.append(('<chain_id_int>', str(Properties().chain_id(self.env))))
        self.assertDiff(file1='msg_eip712.json', file2='msg_eip712.json', replace=replaceList)
        self.assertDiff(file1='msg_personal.json', file2='msg_personal.json', replace=replaceList)
        self.assertDiff(file1='msg_both.json', file2='msg_both.json', replace=replaceList)
