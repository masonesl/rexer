from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Self, override
from lib.char import CharClass
from lib.core import CoreIter


class State(ABC):

    @property
    def transitions(self) -> dict[CharClass, Self]:
        return self.__transitions

    @property
    def final(self) -> bool:
        return self.__final

    @property
    def id(self) -> int:
        return self.__id

    @override
    @abstractmethod
    def __str__(self) -> str: ...

    @override
    def __repr__(self) -> str:
        return str(self)

    def __init__(self, id: int):
        self.__transitions: dict[CharClass, Self] = {}
        self.__final:       bool                  = False
        self.__id:          int                   = id

    def add_transition(self, chrcls: CharClass, next: Self):
        assert chrcls not in self.transitions.keys()

        chrcls.strip(self.transitions.keys())
        self.__transitions[chrcls] = next

    def add_self_transition(self, chrcls: CharClass):
        self.add_transition(chrcls, self)

    def with_self_transition(self, chrcls: CharClass) -> Self:
        self.add_self_transition(chrcls)
        return self

    def with_transition(self, chrcls: CharClass, next: Self) -> Self:
        self.add_transition(chrcls, next)
        return self


class StateMachine[S: State](ABC):

    @property
    def states(self) -> list[S]:
        return self.__states

    @property
    def cursor(self) -> int:
        return self.__cursor

    @override
    @abstractmethod
    def __str__(self) -> str: ...

    @override
    def __repr__(self) -> str:
        return str(self)
    
    @abstractmethod
    def __init__(self, statetype: type[S]):
        self.__statetype: type[S] = statetype
        self.__states:    list[S] = [statetype(0)]
        self.__cursor:    int     = 0

    def new_state(self) -> S:
        state = self.__statetype(len(self.states))
        self.states.append(state)
        return state

    def current_state(self) -> S:
        return self.states[self.cursor]

    def set_cursor(self, id: int):
        assert id >= 0 and id < len(self.states)
        self.__cursor = id

    def reset_cursor(self):
        self.set_cursor(0)
