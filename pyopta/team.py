from constants import UNDEFINED_INT


class Team:
    def __init__(self, team_id: int = UNDEFINED_INT, team_name: str = "") -> None:
        """
        Constructor for the Team class.

        :param team_id: int, optional, the identifier of the team. Default is UNDEFINED_INT.
        :param team_name: str, optional, the name of the team. Default is an empty string.
        :return: None
        """
        self.team_id = team_id
        self.team_name = team_name
