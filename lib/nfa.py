from typing import Self, assert_never, final, override

from lib.char import CharClass
from lib.core import Consts, CoreIter
from lib.quantifier import Quantifier
from lib.state import State, StateMachine
from lib.regex import Regex, RegexUnion


@final
class NfaState(State):

    @property
    def epsilons(self) -> set[Self]:
        return self.__epsilons

    @override
    def __str__(self) -> str:
        ss = [self.__class__.__name__, str(self.id), Consts.OPAREN]

        if len(self.transitions) > 0:
            ss.append("Transitions:")
            (CoreIter(self.transitions.items())
                .foreach(lambda t: ss.append(f"{t[0]}->{t[1].id}")))

        if len(self.epsilons) > 0:
            ss.append("Epsilons:")
            (CoreIter(self.epsilons)
                .foreach(lambda e: ss.append(str(e.id))))

        if self.final:
            ss.append("Final")

        ss.append(Consts.CPAREN)
        return ' '.join(ss)

    def __init__(self, id: int):
        self.__epsilons: set[Self] = set()
        super().__init__(id)

    def add_epsilon_transition(self, next: Self):
        assert next not in self.__epsilons
        self.__epsilons.add(next)

    def with_epsilon_transition(self, next: Self) -> Self:
        self.add_epsilon_transition(next)
        return self

    def get_epsilon_reachable(self) -> set[Self]:
        visited: set[Self] = set()
        to_visit           = [self]

        while len(to_visit) > 0:
            state = to_visit.pop()
            (CoreIter(state.epsilons)
                .foreach(lambda st: to_visit.append(st) if st not in visited else None))
            visited.add(state)

        return visited

    def get_epsilon_transitionable(self) -> dict[CharClass, Self]:
        transitions: dict[CharClass, Self] = {}
        reachable_states = self.get_epsilon_reachable()

        (CoreIter(reachable_states)
            .foreach(lambda st: (
                CoreIter(st.transitions.items())
                    .foreach(lambda t: transitions.update({t[0] : t[1]}))
            ))
        )

        return transitions


@final
class Nfa(StateMachine[NfaState]):

    @override
    def __str__(self) -> str:
        return '\n'.join(CoreIter(self.states).map(lambda s: str(s)))

    def __init__(self):
        super().__init__(NfaState)

    def add_regex(self, regex: Regex):
        for pat in regex.patterns:
            start = self.current_state()

            match pat:
                case Regex() as r:
                    self.add_regex(r)
                case RegexUnion() as u:
                    self.add_regex_union(u)
                case CharClass() as c:
                    self.add_char_class(c)
                case _:
                    assert_never(pat)

            assert self.current_state() is not start

            match pat.quantifier:
                case Quantifier.ONE:
                    pass
                case Quantifier.ZERO_OR_ONE:
                    start.add_epsilon_transition(self.current_state())
                case Quantifier.ZERO_OR_MORE:
                    start.add_epsilon_transition(self.current_state())
                    self.current_state().add_epsilon_transition(start)
                case Quantifier.ONE_OR_MORE:
                    self.current_state().add_epsilon_transition(start)
                case _:
                    assert_never(pat.quantifier)

    def add_regex_union(self, union: RegexUnion):
        split1, split2 = self.new_state(), self.new_state()
        self.current_state().add_epsilon_transition(split1)
        self.current_state().add_epsilon_transition(split2)

        self.set_cursor(split1.id)
        self.add_regex(union.first)
        split1 = self.current_state()

        self.set_cursor(split2.id)
        self.add_regex(union.second)
        split2 = self.current_state()

        join = self.new_state()
        split1.add_epsilon_transition(join)
        split2.add_epsilon_transition(join)

        self.set_cursor(join.id)

    def add_char_class(self, chrcls: CharClass):
        next1, next2 = self.new_state(), self.new_state()
        self.current_state().add_transition(chrcls, next1)
        next1.add_epsilon_transition(next2)

        self.set_cursor(next2.id)

    def with_regex(self, regex: Regex) -> Self:
        self.add_regex(regex)
        return self
