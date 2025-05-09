import requests
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties


# messages for failure
def on_failure_msg(name, oncall, workflow_url):
    embed = {
        "title": "🚨 %s checks failing 🚨" % name,
        "description": "CODE RED - The %s health checks are failing! :face_with_monocle:" % name.to_lower(),
        "color": 15158332,
        "fields": [
            {"name": "Team status", "value": "Panicking", "inline": True},
            {"name": "On-call support", "value": "<%s>" % oncall, "inline": True},
            {"name": "Workflow", "value": "[link](%s)" % workflow_url, "inline": False},

        ],
        "footer": {"text": "E2E Monitoring"},
    }

    data = {
        "content":  "%s checks are failing ... please investigate <%s>" % (name, oncall),
        "username": "E2E Health Checks",
        "embeds": [embed]
    }
    return data


# messages for success
def on_success_msg(name, oncall, workflow_url):
    embed = {
        "title": "🚨 %s checks passing 🚨" % name,
        "description": "CODE GREEN - The %s health checks are passing! :smile:" % name.to_lower(),
        "color": 3066993,
        "fields": [
            {"name": "Team status", "value": "Relaxing", "inline": True},
            {"name": "On-call support", "value": "<%s>" % oncall, "inline": True},
            {"name": "Workflow", "value": "[link](%s)" % workflow_url, "inline": False},
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

    def execute(self):
        self.execute_for(name='Primary gateway', type='health')
        self.execute_for(name='Dexynth gateway', type='health-dexynth')

    def execute_for(self, name, key):
        entries = self.runtype_db.get_last_two_results(self.env, key)

        this_status = True if entries[0][1] == 1 else False
        last_status = True if entries[1][1] == 1 else False
        if not this_status and last_status:
            self.log.info('%s status has changed to failing' % name)
            self.send_alert(name, on_failure_msg)

        elif not last_status and this_status:
            self.log.info('%s status has changed to passing' % name)
            self.send_alert(name, on_success_msg)

        elif last_status and this_status:
            self.log.info('%s in a run of passing checks ... no health change' % name)

        elif not last_status and not this_status:
            self.log.info('%s in a run of failing checks ... no health change' % name)

    def send_alert(self, name, get_msg):
        props = Properties()
        webhook_url = 'https://discord.com/api/webhooks/%s/%s' % (props.monitoring_web_hook_id(self.env),
                                                                  props.monitoring_web_hook_token(self.env))
        response = requests.post(webhook_url, json=get_msg(name, props.monitoring_on_call(self.env),
                                                           props.monitoring_workflow_url(self.env)))

        if response.status_code == 204: self.log.info('Send discord msg successfully')
        else: self.log.warn('Failed to send discord msg')
