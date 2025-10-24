import time, requests
from datetime import datetime, timezone
from pysys.constants import BLOCKED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.utils.support import SupportHelper
from ten.test.persistence.funds import FundsPersistence


def discord_warn_msg(seconds, oncall_id, run_url, environment):
    hour = seconds // 3600
    min = (seconds % 3600) // 60
    description = (
            "CODE YELLOW - Balance has not changed over last **%d hour %d min** interval.\n"
            "This is most likely due to roll ups on the L1 not being produced.\n"
            "Please refer to the workflow run link below for more details.") % (hour, min)
    embed = {
        "title": ":warning: Warning on the sequencer balance not changing :warning:",
        "description": description,
        "color": 16776960,
        "fields": [
            {"name": "Environment", "value": "%s" % environment, "inline": True},
            {"name": "On-call support", "value": "<@%s>" % oncall_id, "inline": True},
            {"name": "Workflow run", "value": "[run](%s)" % run_url, "inline": True},

        ],
        "footer": {"text": "E2E Monitoring"},
    }

    data = {
        "content":  "Warning on the sequencer balance not changing",
        "username": "E2E sequence balance checks",
        "embeds": [embed]
    }
    return data


def epoch_to_utc(epoch_time):
    dt = datetime.fromtimestamp(epoch_time, timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        current_time = int(time.time())
        person = SupportHelper.get_person_on_call(self)
        funds_db = FundsPersistence.init(True, self.user_dir, self.machine_name)

        # get last hours of recorded sequencer balance
        sequencer_address = Properties().sequencer_address(key=self.env)
        entries = funds_db.get_since_time('Sequencer', sequencer_address, self.env, current_time - 14400)
        self.log.info('Performing query with details; ')
        self.log.info('  address: %s' % sequencer_address)
        self.log.info('  environment: %s' % self.env)
        self.log.info('  since time: %s' % epoch_to_utc((current_time - 14400)))

        if len(entries) >= 2:
            time_delta = entries[0][0] - entries[-1][0]
            if time_delta >= 7200:
                self.log.info('Retrieved balances;')
                for entry in entries: self.log.info('  %s %s', epoch_to_utc(entry[0]), entry[1])

                funds_delta = int(entries[0][1]) > int(entries[-1][1])
                if funds_delta == 0:
                    msg = discord_warn_msg(time_delta, props.oncall_discord_id(person), "", self.env)
                    self.send_discord_alert(msg)

            else:
                self.log.warn('Less than 2 hours recorded between retrieved entries ... skipping')

        else:
            self.log.warn('Less than 2 entries recorded over the last 4 hour period ... skipping')

    def send_discord_alert(self, msg):
        props = Properties()
        webhook_url = 'https://discord.com/api/webhooks/%s/%s' % (props.discord_web_hook_id(self.env),
                                                                  props.discord_web_hook_token(self.env))
        response = requests.post(webhook_url, json=msg)

        if response.status_code == 204: self.log.info('Sent discord msg')
        else:
            self.log.warn('Failed to send discord msg')
            self.addOutcome(BLOCKED)