from typing import Self, override
from lib.core import CoreIter, Consts
from lib.nfa import Nfa, NfaState
from lib.state import State, StateMachine


class DfaState(State):

    @override
    def __str__(self) -> str:
        ss = [self.__class__.__name__, str(self.id), Consts.OPAREN]

        if len(self.transitions) > 0:
            ss.append("Transitions:")
            (CoreIter(self.transitions.items())
                .foreach(lambda t: ss.append(f"{t[0]}->{t[1].id}")))

        if self.final:
            ss.append("Final")

        ss.append(Consts.CPAREN)
        return ' '.join(ss)

    def __init__(self, id: int):
        self.__nfa_origins: set[NfaState] = set()
        super().__init__(id)

    def add_nfa_origins(self, states: set[NfaState]):
        self.__nfa_origins.update(states)


class Dfa(StateMachine[DfaState]):

    @classmethod
    def from_nfa(cls, nfa: Nfa) -> Self:
        nfa.reset_cursor()
        sm = cls()
        sm.collect_nfa_states(nfa.current_state())
        return sm

    @override
    def __str__(self) -> str:
        return '\n'.join(CoreIter(self.states).map(lambda s: str(s)))

    def __init__(self):
        super().__init__(DfaState)

    def collect_nfa_states(self, nfa_state: NfaState):
        states      = nfa_state.get_epsilon_reachable()
        transitions = nfa_state.get_epsilon_transitionable()

        self.current_state().add_nfa_origins(states)

        for chrcls, state in transitions.items():
            if state == nfa_state:
                self.current_state().add_self_transition(chrcls)
            else:
                next_state = self.new_state()
                self.current_state().add_transition(chrcls, next_state)
                curr = self.current_state()
                self.set_cursor(next_state.id)
                self.collect_nfa_states(state)
                self.set_cursor(curr.id)

