import requests
from twilio.rest import Client
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties


# messages for failure
def on_failure_msg(name, oncall, workflow_url, environment):
    embed = {
        "title": "🚨 %s checks failing 🚨" % name,
        "description": "CODE RED - The e2e health checks are failing! :face_with_monocle:",
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


def on_still_failing_msg(name, oncall, workflow_url, environment):
    data = {
        "content":  "%s checks are still failing ... please investigate <%s>" % (name, oncall),
        "username": "E2E Health Checks"
    }
    return data


# messages for success
def on_success_msg(name, oncall, workflow_url, environment):
    embed = {
        "title": "🚨 %s checks passing 🚨" % name,
        "description": "CODE GREEN - The e2e health checks are passing! :smile:",
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

    def execute(self):
        if self.RUN_TYPE is None:
            self.log.warn('No run type given ... aborting')
        elif self.RUN_NAME is None:
            self.log.warn('No run name given ... aborting')
        else:
            entries = self.runtype_db.get_last_two_results(self.env, self.RUN_TYPE)
            name = self.RUN_NAME.replace('_',' ')

            if len(entries) == 2:
                this_status = True if entries[0][1] == 1 else False
                last_status = True if entries[1][1] == 1 else False

                if not this_status and last_status:
                    self.log.info('Health status has changed to failing')
                    self.send_discord_alert(name, on_failure_msg)
                    self.send_sms_alert('%s checks are failing' % name)

                elif not last_status and this_status:
                    self.log.info('Health status has changed to passing')
                    self.send_discord_alert(name, on_success_msg)
                    self.send_sms_alert('%s checks are now passing' % name)

                elif last_status and this_status:
                    self.log.info('In a run of passing checks ... no health change')

                elif not last_status and not this_status:
                    self.log.info('In a run of failing checks ... no health change')
                    self.send_discord_alert(name, on_still_failing_msg)

            else:
                self.log.warn('Query on latest outcomes does not have enough entries')

    def send_discord_alert(self, name, get_msg):
        props = Properties()
        webhook_url = 'https://discord.com/api/webhooks/%s/%s' % (props.monitoring_web_hook_id(self.env),
                                                                  props.monitoring_web_hook_token(self.env))
        response = requests.post(webhook_url, json=get_msg(name,
                                                           props.monitoring_on_call(self.env),
                                                           props.monitoring_workflow_url(self.env),
                                                           self.env))

        if response.status_code == 204: self.log.info('Sent discord msg')
        else: self.log.warn('Failed to send discord msg')

    def send_sms_alert(self, msg):
        props = Properties()
        client = Client(props.monitoring_twilio_account(), props.monitoring_twilio_token())
        client.messages.create(
            body = msg,
            from_ = props.monitoring_twilio_from_number(),
            to = props.monitoring_twilio_to_number(),
        )
        self.log.info('Sent SMS msg')