import pytest

from hipaasat.cnf import CNF, Clause, ClauseType, Literal
from hipaasat.solvers import DPLL

def test_single_literal():
    solver = DPLL()
    cnf = CNF([
        Clause(ClauseType.OR, [
            Literal("test")
        ]),
    ])
    solved, result_cnf = solver.solve(cnf)
    assert solved
    assert result_cnf.assigned_literal_count() == result_cnf.unique_literal_count()

def test_single_literal_multiple_clauses():
    solver = DPLL()
    cnf = CNF([
        Clause(ClauseType.OR, [
            Literal("test")
        ]),
        Clause(ClauseType.OR, [
            Literal("test")
        ]),
        Clause(ClauseType.OR, [
            Literal("test")
        ]),
    ])
    solved, result_cnf = solver.solve(cnf)
    assert solved
    assert result_cnf.assigned_literal_count() == result_cnf.unique_literal_count()

def test_single_literal_multiple_clauses_unsolvable():
    solver = DPLL()
    cnf = CNF([
        Clause(ClauseType.OR, [
            Literal("test")
        ]),
        Clause(ClauseType.OR, [
            Literal("test", negated=True)
        ]),
        Clause(ClauseType.OR, [
            Literal("test")
        ]),
    ])
    solved, _ = solver.solve(cnf)
    assert not solved

def test_multiple_literals_single_clause():
    solver = DPLL()
    cnf = CNF([
        Clause(ClauseType.OR, [
            Literal("test"), Literal("test2", negated=True), Literal("test3")
        ]),
    ])
    solved, result_cnf = solver.solve(cnf)
    assert solved
    assert result_cnf.assigned_literal_count() == 1

def test_multiple_literals_multiple_clauses_1():
    solver = DPLL()
    cnf = CNF([
        Clause(ClauseType.OR, [
            Literal("a", negated=True), Literal("b"), Literal("c"),
        ]),
        Clause(ClauseType.OR, [
            Literal("a"), Literal("c"), Literal("d"),
        ]),
        Clause(ClauseType.OR, [
            Literal("a"), Literal("c"), Literal("d", negated=True),
        ]),
        Clause(ClauseType.OR, [
            Literal("a"), Literal("c", negated=True), Literal("d"),
        ]),
        Clause(ClauseType.OR, [
            Literal("a"), Literal("c", negated=True), Literal("d", negated=True),
        ]),
        Clause(ClauseType.OR, [
            Literal("b", negated=True), Literal("c", negated=True), Literal("d"),
        ]),
        Clause(ClauseType.OR, [
            Literal("a", negated=True), Literal("b"), Literal("c", negated=True),
        ]),
        Clause(ClauseType.OR, [
            Literal("a", negated=True), Literal("b", negated=True), Literal("c")
        ]),
    ])
    solved, result_cnf = solver.solve(cnf)
    assert solved
    assert result_cnf.assigned_literal_count() == result_cnf.unique_literal_count()
    
    a = result_cnf.get_literal("a")
    b = result_cnf.get_literal("b")
    c = result_cnf.get_literal("c")
    d = result_cnf.get_literal("d")

    assert a and a.assignment == True
    assert b and b.assignment == True
    assert c and c.assignment == True
    assert d and d.assignment == True

def test_multiple_literals_multiple_clauses_2():
    solver = DPLL()
    cnf = CNF([
        Clause(ClauseType.OR, [
            Literal("lib-1"), Literal("lib-2"), Literal("prog-1", negated=True),
        ]),
        Clause(ClauseType.OR, [
            Literal("lib-2"), Literal("prog-2", negated=True),
        ]),
        Clause(ClauseType.OR, [
            Literal("python-2"), Literal("lib-1", negated=True),
        ]),
        Clause(ClauseType.OR, [
            Literal("python-3"), Literal("lib-2", negated=True),
        ]),
        Clause(ClauseType.OR, [
            Literal("python-3", negated=True)
        ]),
        Clause(ClauseType.OR, [
            Literal("prog-1"), Literal("prog-2"),
        ]),
        Clause(ClauseType.AT_MOST_ONE, [
            Literal("prog-1"), Literal("prog-2"),
        ]),
        Clause(ClauseType.AT_MOST_ONE, [
            Literal("lib-1"), Literal("lib-2"),
        ]),
        Clause(ClauseType.AT_MOST_ONE, [
            Literal("python-2"), Literal("python-3"),
        ]),
    ])

    solved, result_cnf = solver.solve(cnf)
    assert solved
    assert result_cnf.assigned_literal_count() == result_cnf.unique_literal_count()

    prog1 = result_cnf.get_literal("prog-1")
    prog2 = result_cnf.get_literal("prog-2")
    lib1 = result_cnf.get_literal("lib-1")
    lib2 = result_cnf.get_literal("lib-2")
    python2 = result_cnf.get_literal("python-2")
    python3 = result_cnf.get_literal("python-3")

    assert prog1 and prog1.assignment == True
    assert prog2 and prog2.assignment == False
    assert lib1 and lib1.assignment == True
    assert lib2 and lib2.assignment == False
    assert python2 and python2.assignment == True
    assert python3 and python3.assignment == False
