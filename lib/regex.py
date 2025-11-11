from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass
from typing import Self, assert_never, final, override

from lib.char import CharClass
from lib.core import Consts, CoreIter
from lib.quantifier import Quantifier


@final
@dataclass
class RegexUnion:
    first:      "Regex"
    second:     "Regex"
    quantifier: Quantifier = Quantifier.ONE

    @override
    def __str__(self) -> str:
        return f"{self.first}{Consts.UNION}{self.second}{self.quantifier}"
    
    @override
    def __repr__(self) -> str:
        return str(self)

    def set_quantifier(self, quantifier: Quantifier):
        self.quantifier = quantifier


@final
class Regex:

    @override
    def __str__(self) -> str:
        ss: list[str] = [Consts.OPAREN]
        CoreIter(self.__patterns).foreach(lambda p: ss.append(str(p)))
        ss.append(Consts.CPAREN)
        ss.append(self.__quantifier)
        return ''.join(ss)

    @override
    def __repr__(self) -> str:
        return str(self)

    def __init__(self, s: Iterable[str] | CoreIter[str], *, top: bool = True):
        self.__patterns:   "list[Self | CharClass | RegexUnion]" = []
        self.__quantifier: Quantifier = Quantifier.ONE

        match s:
            case CoreIter():
                sit = s
            case Iterable():
                sit = CoreIter(s)
            case _:
                assert_never(s)

        while (ch := sit.next()) is not None and ch != Consts.CPAREN:
            match ch:
                case Consts.OPAREN:
                    self.__patterns.append(self.__class__(sit, top = False))
                case Consts.OBRACK:
                    self.parse_char_class(sit)
                case Consts.BSLASH:
                    self.parse_escape_char(sit)
                case Consts.UNION:
                    union = RegexUnion(deepcopy(self), self.__class__(sit, top = top))
                    self.__patterns.clear()
                    self.__patterns.append(union)
                    if not top:
                        sit.putback()
                case (Consts.ZERO_OR_ONE | Consts.ZERO_OR_MORE | Consts.ONE_OR_MORE) as q:
                    self.__patterns[-1].set_quantifier(Quantifier(q))
                case str(ch):
                    self.__patterns.append(CharClass().with_char(ch))
                case _:
                    assert_never(ch)

        if not top and ch != Consts.CPAREN:
            raise Exception("Unterminated regex group")

    def set_quantifier(self, quantifier: Quantifier):
        self.__quantifier = quantifier

    def parse_escape_char(self, sit: CoreIter[str]):
        match (ch := sit.next()):
            case 'w':
                self.__patterns.append(CharClass().with_alpha().with_numeric())
            case 'd':
                self.__patterns.append(CharClass().with_numeric())
            case 's':
                self.__patterns.append(CharClass().with_whitespace())
            case str(ch):
                self.__patterns.append(CharClass().with_char(ch))
            case None:
                raise Exception("Escape character at the end of regex expression")
            case _:
                assert_never(ch)

    def parse_char_class(self, sit: CoreIter[str]):
        chars: list[str | tuple[str, str]] = [sit.next('\0')]
        assert isinstance(chars[0], str)
        if chars[0] == '\0':
            raise Exception("Empty bracket expression")

        while (ch := sit.next()) is not None and ch != Consts.CBRACK:
            if ch == Consts.DASH:
                if isinstance(prev_ch := chars.pop(), str) and (ch := sit.next()) is not None:
                    chars.append((prev_ch, ch))
                else:
                    raise Exception("Invalid character range in bracket expression")
            else:
                chars.append(ch)

        if ch != Consts.CBRACK:
            raise Exception("Unterminated bracket expression")

        ch_cls = CharClass()
        for ch in chars:
            match ch:
                case str(ch):
                    ch_cls.add_char(ch)
                case tuple((start_ch, end_ch)):
                    ch_cls.add_char_range(start_ch, end_ch)
                case _:
                    assert_never(ch)

        self.__patterns.append(ch_cls)
