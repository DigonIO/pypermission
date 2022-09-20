from typing import Any, cast

import yaml

from pypermission.json.core import Authority as _Authority
from pypermission.json.core import NonSerialData


class Authority(_Authority):
    @staticmethod
    def _serialize_data(*, non_serial_data: NonSerialData) -> str:
        # cast only valid with one argument to dumps
        return cast(str, yaml.safe_dump(non_serial_data))

    @staticmethod
    def _deserialize_data(*, serial_data: str) -> Any:
        return yaml.safe_load(serial_data)
