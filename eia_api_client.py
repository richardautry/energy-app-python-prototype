import requests
from datetime import datetime, timezone, timedelta
from enum import Enum
import json
from dataclasses import dataclass
from utils import convert_camel_to_snake_case

EIA_URL = "https://api.eia.gov/v2/electricity/rto/region-data/data/"


class Frequency(Enum):
    LOCAL_HOURLY = "local-hourly"


class DataType(Enum):
    VALUE = "value"


class Facet(Enum):
    MIDA = "MIDA"


@dataclass
class Data:
    period: str
    respondent: str
    respondent_name: str
    type: str
    type_name: str
    value: int
    value_units: str


@dataclass
class EIAResponse:
    total: int
    date_format: str
    frequency: str
    data: list[Data]
    description: str


@dataclass
class EIAJsonResult:
    response: dict
    request: dict
    api_version: str


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
    ) -> EIAResponse:
        # url = f"{EIA_URL}?api_key={self.api_key}"
        url = EIA_URL
        arg_map = {
            "frequency": frequency.value if frequency else None,
            "data[0]": data_type.value if data_type else None,
            "facets[respondent][]": facet.value if facet else None,
            "start": self._format_datetime(start),
            "end": self._format_datetime(end)
        }
        params = f"api_key={self.api_key}"
        for field, value in arg_map.items():
            if value is not None:
                params += f"&{field}={value}"

        response = requests.get(url, params=params)
        assert response.status_code == 200
        eia_response = self.parse_response(response.json())
        return eia_response

    def parse_response(self, result: dict) -> EIAResponse:
        eia_json_result = EIAJsonResult(
            **self.convert_dict_to_snake_case(result)
        )

        eia_response_dict = self.convert_dict_to_snake_case(eia_json_result.response)
        eia_response_dict["data"] = [Data(**self.convert_dict_to_snake_case(data_item)) for data_item in eia_response_dict.get("data")]
        eia_response = EIAResponse(
            **eia_response_dict
        )
        return eia_response

    @staticmethod
    def convert_dict_to_snake_case(result: dict) -> dict:
        # TODO: Convert to recursive
        return {
            convert_camel_to_snake_case(key).replace("-", "_"): val for key, val in result.items()
        }

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
