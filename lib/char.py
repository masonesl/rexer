from collections.abc import Iterable, Iterator
from copy import copy
from typing import Self, assert_never, cast, final, override

from lib.core import Consts, CoreIter
from lib.quantifier import Quantifier


@final
class CharClass:

    @override
    def __str__(self) -> str:
        if self.wildcard:
            return f"[[{Consts.WILDCARD}]]"

        ss: list[str] = []
        if len(chars := self.group_chars()) > 1 or isinstance(chars[0], tuple):
            ss.append(Consts.OBRACK)

        for ch in chars:
            match ch:
                case str(ch):
                    ss.append(ch)
                case tuple((start_ch, end_ch)):
                    ss.append(f"{start_ch}{Consts.DASH}{end_ch}")
                case _:
                    assert_never(ch)

        if ss[0] == Consts.OBRACK:
            ss.append(Consts.CBRACK)

        ss.append(self.quantifier)

        return ''.join(ss)

    @override
    def __hash__(self) -> int:
        ccpy = cast(list[str | Quantifier | bool], copy(self.chars))
        ccpy.extend((self.quantifier, self.wildcard))
        return hash(tuple(ccpy))

    @override
    def __eq__(self, value: object, /) -> bool:
        assert isinstance(value, "CharClass")
        return ( self.chars      == value.chars      and
                 self.quantifier == value.quantifier and
                 self.wildcard   == value.wildcard )

    @override
    def __repr__(self) -> str:
        return str(self)

    @property
    def chars(self) -> list[str]:
        return self.__chars

    @property
    def quantifier(self) -> Quantifier:
        return self.__quantifier

    @property
    def wildcard(self) -> bool:
        return self.__wildcard

    def __init__(self):
        self.__chars:      list[str]  = []
        self.__quantifier: Quantifier = Quantifier.ONE
        self.__wildcard:   bool       = False

    def __iter__(self) -> Iterator[str]:
        return iter(self.chars)

    def add_char(self, ch: str):
        if len(ch) == 0:
            raise Exception("Cannot add empty string to character class")

        assert len(ch) == 1

        self.__chars.append(ch)
        self.__chars.sort()

    def add_char_range(self, start_ch: str, end_ch: str):
        if not (ord(start_ch) < ord(end_ch)):
            raise Exception("Cannot add character range where the start character is not less than the end character")

        CoreIter(range(ord(start_ch), ord(end_ch) + 1)).foreach(
            lambda ch_n: self.add_char(chr(ch_n))
        )

    def add_alpha(self):
        self.add_char_range('A', 'Z')
        self.add_char('_')
        self.add_char_range('a', 'z')

    def add_numeric(self):
        self.add_char_range('0', '9')

    def add_whitespace(self):
        self.add_char(' ')

    def set_quantifier(self, quantifier: Quantifier):
        self.__quantifier = quantifier

    def set_wildcard(self):
        assert len(self.__chars) == 0
        self.__wildcard = True

    def with_wildcard(self) -> Self:
        self.set_wildcard()
        return self

    def with_quantifier(self, quantifier: Quantifier) -> Self:
        self.set_quantifier(quantifier)
        return self

    def with_whitespace(self) -> Self:
        self.add_whitespace()
        return self

    def with_numeric(self) -> Self:
        self.add_numeric()
        return self

    def with_alpha(self) -> Self:
        self.add_alpha()
        return self

    def with_char_range(self, start_ch: str, end_ch: str) -> Self:
        self.add_char_range(start_ch, end_ch)
        return self

    def with_char(self, ch: str) -> Self:
        self.add_char(ch)
        return self

    def group_chars(self) -> list[str | tuple[str, str]]:
        chars: list[str | tuple[str, str]] = []

        cit = CoreIter(self)
        ch = cit.next()
        while ch is not None:
            start_ch = end_ch = ch
            while (ch := cit.next()) is not None and ord(ch) == ord(end_ch) + 1:
                end_ch = ch

            if start_ch == end_ch:
                chars.append(end_ch)
            else:
                chars.append((start_ch, end_ch))

        return chars

    def strip(self, others: Iterable[Self]):
        (CoreIter(others)
            .foreach(lambda other: (
                CoreIter(other)
                    .filter(lambda ch: ch in self)
                    .foreach(lambda ch: self.remove_char(ch))
            ))
        )

    def remove_char(self, char: str):
        self.__chars.remove(char)
