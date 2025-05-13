import requests
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties


# messages for failure
def discord_failure_msg(name, oncall, workflow_url, environment):
    embed = {
        "title": "🚨 %s checks failing 🚨" % name,
        "description": "CODE RED - The %s checks are failing! :face_with_monocle:" % name,
        "color": 15158332,
        "fields": [
            {"name": "Environment", "value": "%s" % environment, "inline": True},
            {"name": "On-call support", "value": "<%s>" % oncall, "inline": True},
            {"name": "Workflow", "value": "[workflow](%s)" % workflow_url, "inline": True},

        ],
        "footer": {"text": "E2E Monitoring"},
    }

    data = {
        "content":  "%s checks are failing ... please investigate <%s>" % (name, oncall),
        "username": "E2E Health Checks",
        "embeds": [embed]
    }
    return data


def discord_still_failing_msg(name, oncall):
    data = {
        "content":  "%s checks are still failing ... please investigate <%s>" % (name, oncall),
        "username": "E2E Health Checks"
    }
    return data


# messages for success
def discord_success_msg(name, oncall, workflow_url, environment):
    embed = {
        "title": ":white_check_mark: %s checks passing :white_check_mark:" % name,
        "description": "CODE GREEN - The %s checks are passing! :smile:" % name,
        "color": 3066993,
        "fields": [
            {"name": "Environment", "value": "%s" % environment, "inline": True},
            {"name": "On-call support", "value": "<%s>" % oncall, "inline": True},
            {"name": "Workflow", "value": "[workflow](%s)" % workflow_url, "inline": True},
        ],
        "footer": {"text": "E2E Monitoring"},
    }

    data = {
        "content":  "%s checks are passing - system is back to normal" % name,
        "username": "E2E Health Checks",
        "embeds": [embed]
    }
    return data


class PySysTest(TenNetworkTest):
    RUN_TYPE = None
    RUN_NAME = None
    RUN_URL = None

    def execute(self):
        if self.RUN_TYPE is None:
            self.log.warn('No run type given ... aborting')
        elif self.RUN_NAME is None:
            self.log.warn('No run name given ... aborting')
        elif self.RUN_URL is None:
            self.log.warn('No run url given ... aborting')
        else:
            entries = self.runtype_db.get_last_two_results(self.env, self.RUN_TYPE)
            name = self.RUN_NAME.replace('_',' ')

            if len(entries) == 2:
                this_status = True if entries[0][1] == 1 else False
                last_status = True if entries[1][1] == 1 else False

                # have started failing (passed -> failed)
                if last_status and not this_status:
                    msg = '%s checks have started failing, please investigate' % name
                    self.log.info(msg)
                    self.send_call_alert(msg)
                    self.send_sms_alert(msg)
                    self.send_discord_alert(name, discord_failure_msg)

                # have started failing (failed -> passed)
                elif not last_status and this_status:
                    msg = '%s checks are now passing' % name
                    self.log.info(msg)
                    self.send_sms_alert(msg)
                    self.send_discord_alert(name, discord_success_msg)

                # are continuing to pass (passed -> passed)
                elif last_status and this_status:
                    self.log.info('In a run of passing checks ... no change')

                # are continuing to fail (failed -> failed)
                elif not last_status and not this_status:
                    msg = '%s checks are still failing' % name
                    self.log.info(msg)
                    self.send_sms_alert(msg)
                    self.send_discord_alert(name, discord_still_failing_msg)

            else:
                self.log.warn('Query on latest outcomes does not have enough entries')

    def send_discord_alert(self, name, get_msg):
        props = Properties()
        webhook_url = 'https://discord.com/api/webhooks/%s/%s' % (props.monitoring_web_hook_id(self.env),
                                                                  props.monitoring_web_hook_token(self.env))
        response = requests.post(webhook_url, json=get_msg(name,
                                                           props.monitoring_on_call(self.env),
                                                           self.RUN_URL,
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
            self.log.info('Sent SMS msg')
        except:
            self.log.warn('Unable to send SMS message')

    def send_call_alert(self, msg):
        props = Properties()
        try:
            ssml = '<speak><prosody rate="slow">%s</prosody></speak>' % msg
            response = VoiceResponse()
            response.pause(length=1)
            response.say('This is TEN support calling', voice="Polly.Amy")
            response.pause(length=1)
            response.say(ssml, voice="Polly.Amy")
            response.pause(length=1)
            response.say('Check discord support channel for more information', voice="Polly.Amy")

            client = Client(props.monitoring_twilio_account(), props.monitoring_twilio_token())
            client.calls.create(
                twiml=str(response),
                from_=props.monitoring_twilio_from_number(),
                to=props.monitoring_twilio_to_number(),
            )
            self.log.info('Sent call')
        except:
            self.log.warn('Unable to send call')