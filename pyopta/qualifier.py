from typing import Union
from constants import UNDEFINED_INT


class Qualifier:
    def __init__(self, **kwargs) -> None:
        """
        Constructor for the Qualifier class.

        :param kwargs: dictionary, optional, contains values for the properties of the Qualifier object.
        :return: None
        """
        prop_defaults: dict[str, Union[int, str]] = {
            "id": UNDEFINED_INT,
            "qualifier_id": UNDEFINED_INT,
            "value": ""
        }
        self.__dict__.update(prop_defaults)
        self.__dict__.update(kwargs)
