from enum import StrEnum

from lib.core import Consts


class Quantifier(StrEnum):
    ONE          = ''
    ZERO_OR_ONE  = Consts.ZERO_OR_ONE
    ZERO_OR_MORE = Consts.ZERO_OR_MORE
    ONE_OR_MORE  = Consts.ONE_OR_MORE
