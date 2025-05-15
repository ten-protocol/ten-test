import yaml, pytz, os
from datetime import datetime
from pysys.constants import PROJECT


class SupportHelper:

    @classmethod
    def load_rota(cls):
        rota = os.path.join(PROJECT.root, 'utils', 'support', 'rota.yml')
        with open(rota, 'r') as file:
            return yaml.safe_load(file)

    @classmethod
    def get_person_on_call(cls, test):
        rota = cls.load_rota()
        utc = datetime.utcnow().replace(tzinfo=pytz.utc)
        local_time = utc.astimezone(pytz.timezone("Europe/London"))
        day = local_time.strftime("%A")
        time_str = local_time.strftime("%H:%M")

        person = None
        for shift in rota.get(day, []):
            if shift["start"] <= time_str <= shift["end"]:
                person = shift["person"]
        test.log.info('Person on call for %s at %s is %s' % (day, time_str, person))
        return person

