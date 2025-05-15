import requests, time, pytz
from datetime import datetime
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from pysys.constants import FAILED, PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.utils.support import SupportHelper


def greet_by_time(timezone_str='Europe/London'):
    try:
        utc = datetime.utcnow().replace(tzinfo=pytz.utc)
        local_tz = pytz.timezone(timezone_str)
        local_time = utc.astimezone(local_tz)
        hour = local_time.hour
        if 5 <= hour < 12: return "Good morning"
        elif 12 <= hour < 17: return "Good afternoon"
        elif 17 <= hour < 22: return "Good evening"
        else: return "Hello"
    except:
        return "Hello"


# messages for failure
def discord_failure_msg(name, oncall, run_url, environment):
    embed = {
        "title": "🚨 %s checks failing 🚨" % name,
        "description": "CODE RED - The %s checks have started failing! :poop: " % name,
        "color": 15158332,
        "fields": [
            {"name": "Environment", "value": "%s" % environment, "inline": True},
            {"name": "On-call support", "value": "<@%s>" % oncall, "inline": True},
            {"name": "Workflow run", "value": "[run](%s)" % run_url, "inline": True},

        ],
        "footer": {"text": "E2E Monitoring"},
    }

    data = {
        "content":  "%s checks are failing ... " % name,
        "username": "E2E Health Checks",
        "embeds": [embed]
    }
    return data


def discord_still_failing_msg(content, oncall):
    data = {
        "content":  "%s ... " % content,
        "username": "E2E Health Checks"
    }
    return data


# messages for success
def discord_success_msg(name, oncall, run_url, environment):
    embed = {
        "title": ":white_check_mark: %s checks passing :white_check_mark:" % name,
        "description": "CODE GREEN - The %s checks have started passing! :boom: " % name,
        "color": 3066993,
        "fields": [
            {"name": "Environment", "value": "%s" % environment, "inline": True},
            {"name": "On-call support", "value": "<@%s>" % oncall, "inline": True},
            {"name": "Workflow run", "value": "[run](%s)" % run_url, "inline": True},
        ],
        "footer": {"text": "E2E Monitoring"},
    }

    data = {
        "content":  "%s checks are passing ..." % name,
        "username": "E2E Health Checks",
        "embeds": [embed]
    }
    return data


class PySysTest(TenNetworkTest):
    RUN_TYPE = None
    RUN_NAME = None
    RUN_URL = None

    def execute(self):
        props = Properties()

        if self.RUN_TYPE is None:
            self.log.warn('No run type given ... aborting')
        elif self.RUN_NAME is None:
            self.log.warn('No run name given ... aborting')
        elif self.RUN_URL is None:
            self.log.warn('No run url given ... aborting')
        else:
            entries = self.runtype_db.get_last_two_results(self.env, self.RUN_TYPE)
            name = self.RUN_NAME.replace('_',' ')
            person = SupportHelper.get_person_on_call(self)

            if len(entries) == 2:
                this_status = True if entries[0][1] == 1 else False
                last_status = True if entries[1][1] == 1 else False

                # have started failing (passed -> failed)
                if last_status and not this_status:
                    msg = '%s checks have started failing, please investigate' % name
                    self.log.info(msg)
                    self.send_call_alert(msg, person)
                    self.send_sms_alert(msg, person)
                    self.send_discord_alert(discord_failure_msg(name, props.oncall_discord_id(person), self.RUN_URL, self.env))
                    self.addOutcome(FAILED)

                # have started passing (failed -> passed)
                elif not last_status and this_status:
                    msg = '%s checks are now passing' % name
                    self.log.info(msg)
                    self.send_sms_alert(msg, person)
                    self.send_discord_alert(discord_success_msg(name, props.oncall_discord_id(person), self.RUN_URL, self.env))
                    self.addOutcome(PASSED)

                # are continuing to pass (passed -> passed)
                elif last_status and this_status:
                    self.log.info('In a run of passing checks ... no change')
                    self.addOutcome(PASSED)

                # are continuing to fail (failed -> failed)
                elif not last_status and not this_status:
                    msg = '%s checks are still failing' % name

                    # get the last success to work out how long since the last pass
                    entry = self.runtype_db.get_last_result(self.env, self.RUN_TYPE, outcome=1)
                    if entry is not None:
                        seconds = int(time.time()) - int(entry[0])
                        hour = seconds // 3600
                        min = (seconds % 3600) // 60
                        msg = '%s checks are still failing, last success %d hours %d mins ago' % (name, hour, min)

                    self.log.info(msg)
                    self.send_sms_alert(msg, person)
                    self.send_discord_alert(discord_still_failing_msg(msg, props.oncall_discord_id(person)))
                    self.addOutcome(FAILED)

            else:
                self.log.warn('Query on latest outcomes does not have enough entries')

    def send_discord_alert(self, msg):
        props = Properties()
        webhook_url = 'https://discord.com/api/webhooks/%s/%s' % (props.discord_web_hook_id(self.env),
                                                                  props.discord_web_hook_token(self.env))
        response = requests.post(webhook_url, json=msg)

        if response.status_code == 204: self.log.info('Sent discord msg')
        else: self.log.warn('Failed to send discord msg')

    def send_sms_alert(self, msg, person):
        props = Properties()
        tel = props.oncall_telephone(person)
        try:
            client = Client(props.twilio_account(), props.twilio_token())
            client.messages.create(
                body=msg,
                from_=props.twilio_from_number(),
                to=tel,
            )
            self.log.info('Sent SMS msg')
        except:
            self.log.warn('Unable to send SMS message')

    def send_call_alert(self, msg, person):
        props = Properties()
        tel = props.oncall_telephone(person)
        try:
            ssml = '<speak><prosody rate="slow">%s</prosody></speak>' % msg
            response = VoiceResponse()
            response.pause(length=1)
            response.say('%s %s, this is TEN support calling' % (greet_by_time(), person), voice="Polly.Amy")
            response.pause(length=1)
            response.say(ssml, voice="Polly.Amy")
            response.pause(length=1)
            response.say('Check discord support channel for more information', voice="Polly.Amy")

            client = Client(props.twilio_account(), props.twilio_token())
            client.calls.create(
                twiml=str(response),
                from_=props.twilio_from_number(),
                to=tel,
            )
            self.log.info('Sent call')
        except:
            self.log.warn('Unable to send call')