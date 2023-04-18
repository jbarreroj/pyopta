from datetime import date
from typing import Union

from constants import (
    UNDEFINED_INT, UNDEFINED_DATE)


class Game:
    def __init__(self, **kwargs) -> None:
        """
        Constructor for the Game class.

        :param kwargs: dictionary, optional, contains values for the properties of the Game object.
        :return: None
        """
        prop_defaults: dict[str, Union[int, str, date]] = {
            "match_id": UNDEFINED_INT,
            "competition_id": UNDEFINED_INT,
            "competition_name": "",
            "season_id": UNDEFINED_INT,
            "season_name": "",
            "matchday": UNDEFINED_INT,
            "game_date": UNDEFINED_DATE,
            "period_1_start": UNDEFINED_DATE,
            "period_2_start": UNDEFINED_DATE,
            "home_team_id": UNDEFINED_INT,
            "home_team_name": "",
            "home_score": UNDEFINED_INT,
            "away_team_id": UNDEFINED_INT,
            "away_team_name": "",
            "away_score": UNDEFINED_INT,
            "additional_info": ""
        }
        self.__dict__.update(prop_defaults)
        self.__dict__.update(kwargs)

    def __str__(self) -> str:
        """
        Returns a string representation of the Game object.

        :return: str
        """
        return (
            f'{self.competition_name} ({self.season_name}). Matchday {self.matchday}\n'
            f'Date: {self.game_date}\n'
            f'{self.home_team_name} {self.home_score} - {self.away_score} {self.away_team_name}\n'
            f'Additional info: {self.additional_info}'
        )
