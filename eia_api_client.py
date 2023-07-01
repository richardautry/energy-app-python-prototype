import requests
from datetime import datetime, timezone, timedelta
from enum import Enum
import json

EIA_URL = "https://api.eia.gov/v2/electricity/rto/region-data/data/"


class Frequency(Enum):
    LOCAL_HOURLY = "local-hourly"


class DataType(Enum):
    VALUE = "value"


class Facet(Enum):
    MIDA = "MIDA"


class EIAClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_data(
            self,
            frequency: Frequency | None,
            data_type: DataType | None,
            facet: Facet | None,
            start: datetime | None,
            end: datetime | None
    ):
        # url = f"{EIA_URL}?api_key={self.api_key}"
        url = EIA_URL
        arg_map = {
            "frequency": frequency.value if frequency else None,
            "data[0]": data_type.value if data_type else None,
            "facets[respondent][]": facet.value if facet else None,
            "start": self._format_datetime(start),
            "end": self._format_datetime(end)
        }
        params = f"api_key={api_key}"
        for field, value in arg_map.items():
            if value is not None:
                params += f"&{field}={value}"

        response = requests.get(url, params=params)
        return

    @staticmethod
    def _format_datetime(dt: datetime):
        format_str = "%Y-%m-%dT%H:%M:%S-04:00"
        return dt.strftime(format_str)


if __name__ == "__main__":
    with open("config.json", "r") as f:
        config_json = json.load(f)

    api_key = config_json.get("api_key")

    eia_client = EIAClient(api_key)
    eia_client.get_data(
        frequency=Frequency.LOCAL_HOURLY,
        data_type=DataType.VALUE,
        facet=Facet.MIDA,
        start=datetime(2023, 6, 24, tzinfo=timezone(offset=-timedelta(hours=4))),
        end=datetime(2023, 7, 1, tzinfo=timezone(offset=-timedelta(hours=4)))
    )
