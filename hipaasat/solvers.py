from abc import ABC, abstractmethod
import sys

from .cnf import check_consistency, Clause, CNF, Literal, simplify

from typing import Optional, Tuple

class SATSolver(ABC):
    """Abstract class that solves boolean satisfyibility problems."""

    @abstractmethod
    def solve(self, cnf: CNF) -> Tuple[bool, Optional[CNF]]:
        ...

class DPLL(SATSolver):
    """Davis–Putnam–Logemann–Loveland (DPLL) boolean satisfyiblity solver."""

    def solve(self, cnf: CNF) -> Tuple[bool, Optional[CNF]]:
        consistent = check_consistency(cnf)
        if consistent is not None:
            return consistent, cnf
        simplified_cnf = simplify(cnf)
        if simplified_cnf is None:
            return False, cnf
        consistent = check_consistency(simplified_cnf)
        if consistent is not None:
            return consistent, cnf

        # Grab unassigned variable from shortest clause
        shortest_clause = self._find_shortest_nonempty_clause(cnf)
        assert shortest_clause
        lit = self._get_unassigned_literal(shortest_clause)

        solved, result_cnf = self.solve(cnf.assign(lit.name, True))
        if not solved:
            solved, result_cnf = self.solve(cnf.assign(lit.name, False))
        
        return solved, result_cnf

    def _find_shortest_nonempty_clause(self, cnf: CNF) -> Optional[Clause]:
        shortest_clause = None
        shortest_clause_length = sys.maxsize # hopefully there's not a clause with 2^32 or 2^64 literals...
        for c in cnf:
            if c.unassigned_literal_count() < shortest_clause_length and c.unassigned_literal_count() > 0:
                shortest_clause = c
                shortest_clause_length = c.unassigned_literal_count()
        return shortest_clause

    def _get_unassigned_literal(self, clause: Clause) -> Literal:
        literals = clause.get_unassigned_literals()
        return literals[0]
