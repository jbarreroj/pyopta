from constants import UNDEFINED_INT


class Player:
    def __init__(self, player_id: int = UNDEFINED_INT, team_id: int = UNDEFINED_INT,
                 match_position: str = "", first: str = "", last: str = "",
                 known: str = "") -> None:
        """
        Constructor for the Player class.

        :param player_id: int, optional, the identifier of the player. Default is UNDEFINED_INT.
        :param team_id: int, optional, the identifier of the team the player belongs to. Default is UNDEFINED_INT.
        :param match_position: str, optional, the position of the player in a match. Default is an empty string.
        :param first: str, optional, the first name of the player. Default is an empty string.
        :param last: str, optional, the last name of the player. Default is an empty string.
        :param known: str, optional, name by which the player is known. Default is an empty string.
        :return: None
        """
        self.player_id = player_id
        self.team_id = team_id
        self.match_position = match_position
        self.first = first
        self.last = last
        self.known = known
