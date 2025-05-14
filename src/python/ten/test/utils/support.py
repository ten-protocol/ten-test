import yaml, pytz
from datetime import datetime


def load_rota(filename="support_rota.yaml"):
    with open(filename, 'r') as file:
        return yaml.safe_load(file)


def get_person_on_call(rota, dt_utc):
    uk_tz = pytz.timezone("Europe/London")
    local_dt = dt_utc.astimezone(uk_tz)

    day = local_dt.strftime("%A")
    time_str = local_dt.strftime("%H:%M")

    for shift in rota.get(day, []):
        if shift["start"] <= time_str <= shift["end"]:
            return shift["person"]
    return None


if __name__ == "__main__":
    rota = load_rota()
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    person = get_person_on_call(rota, now_utc)
