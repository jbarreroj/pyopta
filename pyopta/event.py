from datetime import date
from typing import Union

from constants import (
    UNDEFINED_INT, UNDEFINED_FLOAT, UNDEFINED_DATE)


class Event:
    def __init__(self, **kwargs) -> None:
        """
        Constructor for the Event class.

        :param kwargs: dictionary, optional, contains values for the properties of the Event object.
        :return: None
        """
        prop_defaults: dict[str, Union[int, float, date, list]] = {
            "id": UNDEFINED_INT,
            "event_id": UNDEFINED_INT,
            "type_id": UNDEFINED_INT,
            "period_id": UNDEFINED_INT,
            "min": UNDEFINED_INT,
            "sec": UNDEFINED_INT,
            "team_id": UNDEFINED_INT,
            "player_id": UNDEFINED_INT,
            "outcome": UNDEFINED_INT,
            "assist": UNDEFINED_INT,
            "keypass": UNDEFINED_INT,
            "x": UNDEFINED_FLOAT,
            "y": UNDEFINED_FLOAT,
            "timestamp": UNDEFINED_DATE,
            "last_modified": UNDEFINED_DATE,
            "qualifiers_list": []
        }
        self.__dict__.update(prop_defaults)
        self.__dict__.update(kwargs)
