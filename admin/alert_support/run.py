import requests, time, pytz
from datetime import datetime
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from pysys.constants import BLOCKED
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
def discord_failure_msg(name, oncall_id, all_ids, run_url, environment):
    embed = {
        "title": "🚨 %s checks failing 🚨" % name,
        "description": "CODE RED - The %s checks have started failing! :poop: " % name,
        "color": 15158332,
        "fields": [
            {"name": "Environment", "value": "%s" % environment, "inline": True},
            {"name": "On-call support", "value": "<@%s>" % oncall_id, "inline": True},
            {"name": "Workflow run", "value": "[run](%s)" % run_url, "inline": True},

        ],
        "footer": {"text": "E2E Monitoring"},
    }

    data = {
        "content":  "%s checks are failing %s" % (name, (' '.join(['<@%s>' % x for x in all_ids]))),
        "username": "E2E %s checks" % name,
        "embeds": [embed]
    }
    return data


def telegram_failure_msg(name, oncall, run_url, environment, channel_id):
    message = (
        f"🚨 *{name} checks failing* 🚨\n"
        f"CODE RED - The *{name}* checks have started failing!\n"
        f"*Environment:* {environment}\n"
        f"*On-call support:* {oncall}\n"
        f"*Workflow run:* [View run]({run_url})\n"
    )

    data = {
        "chat_id": channel_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    return data


def discord_still_failing_msg(name, content, all_ids):
    data = {
        "content":  "%s %s" % (content, (' '.join(['<@%s>' % x for x in all_ids]))),
        "username": "E2E %s checks" % name
    }
    return data


def telegram_still_failing_msg(content, channel_id):
    data = {
        "chat_id": channel_id,
        "text": content,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    return data


# messages for success
def discord_success_msg(name, oncall_id, all_ids, run_url, environment):
    embed = {
        "title": ":white_check_mark: %s checks passing :white_check_mark:" % name,
        "description": "CODE GREEN - The %s checks have started passing! :boom: " % name,
        "color": 3066993,
        "fields": [
            {"name": "Environment", "value": "%s" % environment, "inline": True},
            {"name": "On-call support", "value": "<@%s>" % oncall_id, "inline": True},
            {"name": "Workflow run", "value": "[run](%s)" % run_url, "inline": True},
        ],
        "footer": {"text": "E2E Monitoring"},
    }

    data = {
        "content":  "%s checks are passing %s" % (name, (' '.join(['<@%s>' % x for x in all_ids]))),
        "username": "E2E %s checks" % name,
        "embeds": [embed]
    }
    return data


def telegram_success_msg(name, oncall, run_url, environment, channel_id):
    message = (
        f"✅ *{name} checks passing* ✅\n"
        f"CODE GREEN - The *{name}* checks have started passing!\n"
        f"*Environment:* {environment}\n"
        f"*On-call support:* {oncall}\n"
        f"*Workflow run:* [View run]({run_url})\n"
    )

    data = {
        "chat_id": channel_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    return data


class PySysTest(TenNetworkTest):
    RUN_TYPE = None
    RUN_NAME = None
    RUN_URL = None
    TWILIO_DISABLED = True
    DISCORD_DISABLED = True
    TELEGRAM_DISABLED = False

    def execute(self):
        props = Properties()

        if self.RUN_TYPE is None:
            self.log.warn('No run type given ... aborting')
        elif self.RUN_NAME is None:
            self.log.warn('No run name given ... aborting')
        elif self.RUN_URL is None:
            self.log.warn('No run url given ... aborting')
        else:
            name = self.RUN_NAME.replace('_',' ')
            person = SupportHelper.get_person_on_call(self)
            entries = self.runtype_db.get_last_num_results(self.env, self.RUN_TYPE, 3)

            # health checks run every 15 min, true is a pass, false is a fail - decision table below;
            #
            # | t-00  |  t-15 |  t-30 |    Action                 | Call   | SMS    | Discord / Telegram
            # |-------|-------|-------|------------------------------------------------------------------------
            # | false | true  |       | started failing           |        |        | failure_msg
            # | false | false | true  | started and still failing | oncall |        | still_failing_msg
            # | false | false | false | still failing             |        | oncall | still_failing_msg
            # | true  | false |       | started passing           |        | oncall | success_msg

            if len(entries) == 3:
                t00 = True if entries[0][1] == 1 else False
                t15 = True if entries[1][1] == 1 else False
                t30 = True if entries[2][1] == 1 else False

                # started failing
                if not t00 and t15:
                    msg = '%s checks have started failing, please investigate' % name
                    self.log.info(msg)
                    self.send_discord_alert(discord_failure_msg(name, props.oncall_discord_id(person),
                                                                props.all_discord_ids(), self.RUN_URL, self.env))
                    self.send_telegram_message(telegram_failure_msg(name, person, self.RUN_URL, self.env,
                                                                    props.telegram_channel_id(self.env)))

                # started failing and still failing
                elif not t00 and not t15 and t30:
                    msg = '%s checks have failed twice since the last success, please investigate' % name
                    self.send_call_alert(msg, person)

                    # get the last success to work out how long since the last pass
                    entry = self.runtype_db.get_last_result(self.env, self.RUN_TYPE, outcome=1)
                    if entry is not None:
                        seconds = int(time.time()) - int(entry[0])
                        hour = seconds // 3600
                        min = (seconds % 3600) // 60
                        msg = '%s checks are still failing, last success %d hours %d mins ago' % (name, hour, min)

                    self.log.info(msg)
                    self.send_discord_alert(discord_still_failing_msg(name, msg, props.all_discord_ids()))
                    self.send_telegram_message(telegram_still_failing_msg(msg, props.telegram_channel_id(self.env)))

                # still on a failing run
                elif not t00 and not t15 and not t30:
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
                    self.send_discord_alert(discord_still_failing_msg(name, msg, props.all_discord_ids()))
                    self.send_telegram_message(telegram_still_failing_msg(msg, props.telegram_channel_id(self.env)))

                # started passing
                elif t00 and not t15:
                    msg = '%s checks are now passing' % name
                    self.log.info(msg)
                    self.send_sms_alert(msg, person)
                    self.send_discord_alert(discord_success_msg(name, props.oncall_discord_id(person),
                                                                props.all_discord_ids(), self.RUN_URL, self.env))
                    self.send_telegram_message(telegram_success_msg(name, person, self.RUN_URL, self.env,
                                                                    props.telegram_channel_id(self.env)))

                # still on a passing run
                elif t00 and t15:
                    self.log.info('In a run of passing checks ... no change')

            else:
                self.log.warn('Query on latest outcomes does not have enough entries')

    def send_discord_alert(self, msg):
        if self.DISCORD_DISABLED: return

        props = Properties()
        webhook_url = 'https://discord.com/api/webhooks/%s/%s' % (props.discord_web_hook_id(self.env),
                                                                  props.discord_web_hook_token(self.env))
        response = requests.post(webhook_url, json=msg)

        if response.status_code == 204: self.log.info('Sent discord msg')
        else:
            self.log.warn('Failed to send discord msg')
            self.addOutcome(BLOCKED)

    def send_telegram_message(self, msg):
        if self.TELEGRAM_DISABLED: return

        props = Properties()
        url = 'https://api.telegram.org/bot%s/sendMessage' % props.telegram_bot_token(self.env)

        response = requests.post(url, json=msg)

        if response.status_code == 200: self.log.info('Sent telegram msg')
        else:
            self.log.warn('Failed to send telegram msg')
            self.addOutcome(BLOCKED)

    def send_sms_alert(self, msg, person):
        if self.TWILIO_DISABLED: return

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
        except Exception as e:
            self.log.warn('Unable to send SMS message: %s', e)
            self.addOutcome(BLOCKED)

    def send_call_alert(self, msg, person):
        if self.TWILIO_DISABLED: return

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
        except Exception as e:
            self.log.warn('Unable to send SMS message: %s', e)
            self.addOutcome(BLOCKED)