from enum import Enum


class Operator(Enum):
    """
    Enum class for the comparison operators used in queries.

    Each operator has a string representation that can be used in the query syntax.
    """
    EQ: str = "equal"
    NEQ: str = "not_equal"
    LT: str = "less_than"
    LTE: str = "less_than_or_equal"
    GT: str = "greater_than"
    GTE: str = "greater_than_or_equal"
    BW: str = "between"
    IN: str = "in"
    NIN: str = "not_in"
    QIN: str = "qualifier_in"
    QNIN: str = "qualifiers_not_in"
