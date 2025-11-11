from collections.abc import Iterable, Iterator
from typing import Callable, final


@final
class Consts:

    # Add these punctuators because nvim or treesitter doesn't
    # like when there is an opening bracket without a closing one.
    OPAREN = '('
    CPAREN = ')'
    OBRACK = '['
    CBRACK = ']'
    OCURLY = '{'
    CCURLY = '}'

    BSLASH = '\\'

    UNION = '|'

    DASH = '-'

    ZERO_OR_ONE  = '?'
    ZERO_OR_MORE = '*'
    ONE_OR_MORE  = '+'


@final
class CoreIter[T]:
    def __init__(self, obj: Iterable[T]):
        self.__obj:  Iterable[T] = obj
        self.__iter: Iterator[T] = iter(obj)
        self.__prev: T | None    = None
        self.__next: T | None    = None

    def __iter__(self) -> Iterator[T]:
        return self.__iter

    def __next__(self) -> T:
        return next(self.__iter)

    def putback(self):
        self.__next = self.__prev

    def next[D](self, default: D = None) -> T | D:
        if self.__next is not None:
            n = self.__next
            self.__next = None
            return n

        try:
            self.__prev = next(self)
            return self.__prev
        except StopIteration:
            return default

    def foreach(self, fn: Callable[[T], None]):
        for e in self:
            fn(e)

    def map[R](self, fn: Callable[[T], R]) -> "CoreIter[R]":
        new: list[R] = []
        self.foreach(lambda e: new.append(fn(e)))
        return CoreIter(new)

    def collect[N](self, newtype: Callable[[Iterator[T]], N]) -> N:
        return newtype(self)

    def all(self, fn: Callable[[T], bool] = bool) -> bool:
        for e in self:
            if not fn(e):
                return False
        return True

    def any(self, fn: Callable[[T], bool] = bool) -> bool:
        for e in self:
            if fn(e):
                return True
        return False


def foreach[T](fn: Callable[[T], None], obj: Iterable[T]):
    CoreIter(obj).foreach(fn)


def allfn[T](fn: Callable[[T], bool], obj: Iterable[T]) -> bool:
    return CoreIter(obj).all(fn)


def anyfn[T](fn: Callable[[T], bool], obj: Iterable[T]) -> bool:
    return CoreIter(obj).any(fn)
