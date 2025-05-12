import requests, json, time
from web3 import Web3
from twilio.rest import Client
from pysys.constants import FAILED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties


def on_failure_msg(account, funds, threshold, oncall, workflow_url, environment):
    embed = {
        "title": "🚨 %s account funds of %d are below threshold %d 🚨" % (account, funds, threshold),
        "description": "CODE RED - Account is running out of funds! :face_with_monocle:",
        "color": 15158332,
        "fields": [
            {"name": "Environment", "value": "%s" % environment, "inline": True},
            {"name": "Account", "value": account, "inline": True},
            {"name": "Funds", "value": "%d" % funds, "inline": True},
            {"name": "Threshold", "value": "%d" % threshold, "inline": True},
            {"name": "On-call support", "value": "<%s>" % oncall, "inline": True},
            {"name": "Workflow", "value": "[workflow](%s)" % workflow_url, "inline": True},
        ],
        "footer": {"text": "E2E Monitoring"},
    }

    data = {
        "content":  "%s account is running out of funds ... please investigate <%s>" % (account, oncall),
        "username": "E2E Health Checks",
        "embeds": [embed]
    }
    return data


class PySysTest(TenNetworkTest):
    L1_THRESHOLD = 5
    L2_THRESHOLD = 25

    def execute(self):
        current_time = int(time.time())

        network = self.get_l1_network_connection(self.env)
        url = network.connection_url()
        web3 = Web3(Web3.HTTPProvider(url))

        sequencer_address = Properties().sequencer_address(key=self.env)
        sequencer_balance = web3.from_wei(web3.eth.get_balance(sequencer_address), 'ether')
        self.log.info('Sequencer account %s balance %.9f ETH', sequencer_address, sequencer_balance)

        validator1_address = Properties().validator1_address(key=self.env)
        validator1_balance = web3.from_wei(web3.eth.get_balance(validator1_address), 'ether')
        self.log.info('Validator 1 account %s balance %.9f ETH', validator1_address, validator1_balance)

        validator2_address = Properties().validator2_address(key=self.env)
        validator2_balance = web3.from_wei(web3.eth.get_balance(validator2_address), 'ether')
        self.log.info('Validator 2 account %s balance %.9f ETH', validator2_address, validator2_balance)

        deployer_address = Properties().l1_deployer_address(key=self.env)
        deployer_balance = web3.from_wei(web3.eth.get_balance(deployer_address), 'ether')
        self.log.info('Deployer account %s balance %.9f ETH', deployer_address, deployer_balance)

        faucet_address = Properties().faucet_address(key=self.env)
        faucet_balance_wei = self.get_faucet_balance()
        faucet_balance_eth = web3.from_wei(faucet_balance_wei, 'ether')
        self.log.info('Faucet balance %.9f ETH', faucet_balance_eth)
        self.funds_db.insert_funds('Faucet', faucet_address, self.env, current_time, faucet_balance_wei)

        if sequencer_balance < self.L1_THRESHOLD:
            msg = 'Sequencer account funds of %d are below threshold %d' % (sequencer_balance, self.L1_THRESHOLD)
            self.send_discord_alert('Sequencer', sequencer_balance, self.L1_THRESHOLD)
            self.send_sms_alert(msg)
            self.addOutcome(FAILED, outcomeReason=msg)

        if validator1_balance < self.L1_THRESHOLD:
            msg = 'Validator1 account funds of %d are below threshold %d' % (validator1_balance, self.L1_THRESHOLD)
            self.send_discord_alert('Validator1', validator1_balance, self.L1_THRESHOLD)
            self.send_sms_alert(msg)
            self.addOutcome(FAILED, outcomeReason=msg)

        if validator2_balance < self.L1_THRESHOLD:
            msg = 'Validator2 account funds of %d are below threshold %d' % (validator2_balance, self.L1_THRESHOLD)
            self.send_discord_alert('Validator2', validator2_balance, self.L1_THRESHOLD)
            self.send_sms_alert(msg)
            self.addOutcome(FAILED, outcomeReason=msg)

        if deployer_balance < self.L1_THRESHOLD:
            msg = 'Deployer account funds of %d are below threshold %d' % (deployer_balance, self.L1_THRESHOLD)
            self.send_discord_alert('Deployer', deployer_balance, self.L1_THRESHOLD)
            self.send_sms_alert(msg)
            self.addOutcome(FAILED, outcomeReason=msg)

        if faucet_balance_eth < self.L2_THRESHOLD:
            msg = 'Faucet account funds of %d are below threshold %d' % (faucet_balance_eth, self.L2_THRESHOLD)
            self.send_sms_alert(msg)
            self.send_call_alert(msg)
            self.addOutcome(FAILED, outcomeReason=msg)
            self.send_discord_alert('Faucet', faucet_balance_eth, self.L2_THRESHOLD)

    def get_faucet_balance(self):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        url = '%s/balance' % Properties().faucet_host(self.env)
        response = requests.get(url, headers=headers)
        response_data = json.loads(response.text)
        return int(response_data.get('balance'))

    def send_discord_alert(self, account, funds, threshold):
        props = Properties()
        webhook_url = 'https://discord.com/api/webhooks/%s/%s' % (props.monitoring_web_hook_id(self.env),
                                                                  props.monitoring_web_hook_token(self.env))
        response = requests.post(webhook_url, json=on_failure_msg(account, funds, threshold,
                                                                  props.monitoring_on_call(self.env),
                                                                  props.monitoring_funds_check_workflow(self.env),
                                                                  self.env))

        if response.status_code == 204: self.log.info('Sent discord msg')
        else: self.log.warn('Failed to send discord msg')

    def send_sms_alert(self, msg):
        props = Properties()
        try:
            client = Client(props.monitoring_twilio_account(), props.monitoring_twilio_token())
            client.messages.create(
                body=msg,
                from_=props.monitoring_twilio_from_number(),
                to=props.monitoring_twilio_to_number(),
            )
            self.log.info('Sent SMS message')
        except:
            self.log.warn('Unable to send SMS message')

    def send_call_alert(self, msg):
        props = Properties()
        try:
            client = Client(props.monitoring_twilio_account(), props.monitoring_twilio_token())
            client.calls.create(
                twiml='<Response><Say voice="Polly.Amy">%s</Say></Response>' % msg,
                from_=props.monitoring_twilio_from_number(),
                to=props.monitoring_twilio_to_number(),
            )
            self.log.info('Sent call')
        except:
            self.log.warn('Unable to send call')