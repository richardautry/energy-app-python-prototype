from eia_api_client import Data
from datetime import datetime
import asyncio
from kasa import Discover


def get_charge_start_time(charge_time: int, data: list[Data]) -> datetime:
    """
    Given demand data per hour,
    Returns the start datetime to use the entire charge time at the lowest demand (cost) level
    Runs in O(n) time
    :param charge_time: int
    :param data: list[Data]
    :return: datetime
    """
    charge_time_start_index = None
    for i in range(0, len(data) - charge_time + 1):
        sum_demand = sum([data_item.value for data_item in data[i:i + charge_time]])
        if not charge_time_start_index:
            charge_time_start_index = (i, sum_demand)
        elif sum_demand < charge_time_start_index[1]:
            charge_time_start_index = (i, sum_demand)
    return data[charge_time_start_index[0]].period_datetime


if __name__ == "__main__":
    """
    This will find all devices and turn the Test device off
    """
    found_devices = asyncio.run(Discover.discover())
    test_device = list(filter(lambda device: device.alias == "Test", list(found_devices.values())))[0]
    print(f"Test is on {test_device.is_on}")

    asyncio.run(test_device.turn_off())
