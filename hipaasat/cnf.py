from collections import OrderedDict
from enum import Enum

from typing import Any, Dict, Iterable, Iterator, List, Optional, Set

__all__ = [
    "check_clause_consistency",
    "check_at_most_one_clause_consistency",
    "check_consistency",
    "check_or_clause_consistency",
    "Clause",
    "ClauseType",
    "CNF",
    "Literal",
    "simplify",
]

class Literal(object):
    def __init__(self, name: str, negated: bool = False, assignment: bool = None) -> None:
        self._name = name
        self._negated = negated
        self._assignment = assignment

    def __eq__(self, other: Any) -> bool:
        if isinstance(self, Literal):
            return (
                self.name == other.name and
                self.negated == other.negated and
                self.assignment == other.assignment
            )
        return NotImplemented

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def negated(self) -> bool:
        return self._negated
    
    @property
    def assignment(self) -> Optional[bool]:
        return self._assignment
    
    @property
    def value(self) -> Optional[bool]:
        if self.assignment is None:
            return None
        return self.negated ^ self.assignment
    
    def assign(self, value: bool, inplace: bool = False) -> "Literal":
        if inplace:
            self._assignment = value
            ret = self
        else:
            ret = Literal(self.name, self.negated, value)
        return ret

    def copy(self) -> "Literal":
        return Literal(self.name, self.negated, self.assignment)
    
    def is_assigned(self) -> bool:
        return self._assignment is not None
    
    def make_false(self, inplace: bool = False) -> "Literal":
        return self.assign(self.negated & True, inplace=inplace)
    
    def make_true(self, inplace: bool = False) -> "Literal":
        return self.assign(self.negated ^ True, inplace=inplace)

class ClauseType(Enum):
    AT_MOST_ONE = "AtMostOne"
    OR = "OR"

class Clause(object):    
    def __init__(self, clause_type: ClauseType, literals: Iterable[Literal]) -> None:
        seen: Set[str] = set()
        for lit in literals:
            if lit.name in seen:
                raise ValueError("Two or more literals with the same name")
            seen.add(lit.name)

        self._clause_type = clause_type
        self._literals = OrderedDict([(lit.name, lit) for lit in literals])
        self._assigned: Dict[str, Literal] = {lit.name: lit for lit in self._literals.values() if lit.is_assigned()}
        self._unassigned: Dict[str, Literal] = {lit.name: lit for lit in self._literals.values() if not lit.is_assigned()}
    
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Clause):
            equal = self.type == other.type
            for lit in self:
                other_lit = other.get_literal(lit.name)
                equal &= lit == other_lit
            return equal
        return NotImplemented
    
    def __iter__(self) -> Iterator[Literal]:
        return iter(self._literals.values())

    def __len__(self) -> int:
        return len(self._literals)

    @property
    def type(self) -> ClauseType:
        return self._clause_type

    def assign(self, name: str, value: bool, inplace: bool = False) -> "Clause":
        if inplace:
            lit = self._literals.get(name)
            if lit:
                lit.assign(value, inplace=True)
                if lit.name in self._unassigned:
                    del self._unassigned[lit.name]
                    self._assigned[lit.name] = lit
            ret = self
        else:
            literals = (lit.assign(value, inplace=False) if lit.name == name else lit for lit in self._literals.values())
            ret = Clause(self.type, literals)
        return ret

    def assigned_literal_count(self) -> int:
        return len(self._assigned)

    def copy(self) -> "Clause":
        return Clause(self.type, self._literals.values())

    def get_literal(self, name: str) -> Optional[Literal]:
        return self._literals.get(name)

    def get_assigned_literals(self) -> List[Literal]:
        return list(self._assigned.values())

    def get_unassigned_literals(self) -> List[Literal]:
        return list(self._unassigned.values())
    
    def remove_literal(self, name: str, inplace: bool = False) -> "Clause":
        if inplace:
            self._literals.pop(name, None)
            self._assigned.pop(name, None)
            self._unassigned.pop(name, None)
            ret = self
        else:
            literals = (lit for lit in self._literals.values() if lit.name != name)
            ret = Clause(self.type, literals)
        return ret

    def unassigned_literal_count(self) -> int:
        return len(self._unassigned)

def check_clause_consistency(clause: Clause) -> Optional[bool]:
    if clause.type == ClauseType.AT_MOST_ONE:
        return check_at_most_one_clause_consistency(clause)
    elif clause.type == ClauseType.OR:
        return check_or_clause_consistency(clause)
    else:
        raise ValueError("unknown clause type {}".format(clause.type))

def check_at_most_one_clause_consistency(clause: Clause) -> Optional[bool]:
    if clause.type != ClauseType.AT_MOST_ONE:
        raise ValueError("clause must be of type {}".format(ClauseType.AT_MOST_ONE))
    count = 0
    incomplete = False
    for lit in clause:
        if lit.value is None:
            incomplete = True
        else:
            count += lit.value
        if count > 1:
            return False
    return None if incomplete else True

def check_or_clause_consistency(clause: Clause) -> Optional[bool]:
    if clause.type != ClauseType.OR:
        raise ValueError("clause must be of type {}".format(ClauseType.OR))
    incomplete = False
    for lit in clause:
        if lit.value is None:
            incomplete = True
        elif lit.value:
            return True
    return None if incomplete else False

class CNF(object):
    def __init__(self, clauses: Iterable[Clause]) -> None:
        self._clauses = list(clauses)

    def __iter__(self) -> Iterator[Clause]:
        return iter(self._clauses)

    def __len__(self) -> int:
        return len(self._clauses)

    def assign(self, name: str, value: bool, inplace: bool = False) -> "CNF":
        if inplace:
            for c in self:
                c.assign(name, value, inplace=True)
            ret = self
        else:
            clone = self.copy()
            clone.assign(name, value, inplace=True)
            ret = clone
        return ret

    def assigned_literal_count(self) -> int:
        names: Set[str] = set()
        for c in self:
            for lit in c.get_assigned_literals():
                names.add(lit.name)
        return len(names)

    def copy(self) -> "CNF":
        return CNF(self._clauses)

    def get_literal(self, name: str) -> Optional[Literal]:
        duplicates: List[Literal] = []
        for c in self:
            lit = c.get_literal(name)
            if lit:
                duplicates.append(lit)

        exemplar = duplicates.pop()
        while duplicates:
            for lit in duplicates:
                assert exemplar.assignment == lit.assignment
            exemplar = duplicates.pop()
        
        return exemplar

    def unique_literal_count(self) -> int:
        names: Set[str] = set()
        for c in self:
            for lit in c:
                names.add(lit.name)
        return len(names) 

def check_consistency(cnf: CNF) -> Optional[bool]:
    result = True
    incomplete = False
    for c in cnf:
        r = check_clause_consistency(c)
        if r is None:
            incomplete = True
        else:
            result &= r
        if not result:
            # no need to check any of the remaining clauses as this clause is empty
            # and thus the whole statement is inconsistent
            return False
    return None if incomplete else True

def simplify(cnf: CNF, inplace: bool = False) -> Optional[CNF]:
    if inplace:
        ret = _simplify_inplace(cnf)
    else:
        clone = cnf.copy()
        ret = _simplify_inplace(clone)
    return ret

def _simplify_inplace(cnf: CNF) -> Optional[CNF]:
    unit_clauses = [c for c in cnf if c.unassigned_literal_count() == 1]
    while unit_clauses:
        clause = unit_clauses.pop(0)
        literals = clause.get_unassigned_literals()
        assert len(literals) == 1

        literal = literals[0]
        literal.make_true(inplace=True)

        assert literal.assignment is not None
        for c in cnf:
            c.assign(literal.name, literal.assignment, inplace=True)
        consistent = check_consistency(cnf)
        if consistent == False:
            return None
        
        unit_clauses = [c for c in cnf if c.unassigned_literal_count() == 1]
    return cnf
