from enum import Enum


class Period(Enum):
    ALLTIME = "overall"
    WEEK = "7day"
    MONTH = "1month"
    MONTHS3 = "3month"
    MONTHS6 = "6month"
    YEAR = "12month"
