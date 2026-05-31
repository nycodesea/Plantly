import pandas as pd
from config import TZ


def get_now():
    now = pd.Timestamp.now(tz=TZ)

    return {
        "now": now,
        "hour": now.floor("h"),
        "day": now.normalize(),
    }
