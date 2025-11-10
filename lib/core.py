from collections.abc import Iterable, Iterator
from typing import Callable, final


@final
class CoreIter[T]:
    def __init__(self, obj: Iterable[T]):
        self.__obj:  Iterable[T] = obj
        self.__iter: Iterator[T] = iter(obj)

    def __iter__(self) -> Iterator[T]:
        return self.__iter

    def __next__(self) -> T:
        return next(self.__iter)

    def next[D](self, default: D = None) -> T | D:
        try:
            return next(self)
        except StopIteration:
            return default

    def foreach(self, fn: Callable[[T], None]):
        for e in self:
            fn(e)

    def map[R](self, fn: Callable[[T], R]) -> 'CoreIter[R]':
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
