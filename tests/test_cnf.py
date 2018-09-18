import pytest

from hipaasat.cnf import check_consistency, check_clause_consistency, Clause, ClauseType, CNF, Literal

def test_or_clause_consistency_single_literal():
    oc = Clause(ClauseType.OR, [
        Literal("test")
    ])
    assert check_clause_consistency(oc) is None

    oc = Clause(ClauseType.OR, [
        Literal("test", assignment=True)
    ])
    assert check_clause_consistency(oc)

    oc = Clause(ClauseType.OR, [
        Literal("test", assignment=False)
    ])
    assert check_clause_consistency(oc) == False

    oc = Clause(ClauseType.OR, [
        Literal("test", negated=True, assignment=False)
    ])
    assert check_clause_consistency(oc)

    oc = Clause(ClauseType.OR, [
        Literal("test", negated=True, assignment=True)
    ])
    assert check_clause_consistency(oc) == False

def test_or_clause_consistency_multiple_literals():
    oc = Clause(ClauseType.OR, [
        Literal("1"), Literal("2")
    ])
    assert check_clause_consistency(oc) is None

    oc = Clause(ClauseType.OR, [
        Literal("1", assignment=True), Literal("2")
    ])
    assert check_clause_consistency(oc)

    oc = Clause(ClauseType.OR, [
        Literal("1", assignment=False), Literal("2", assignment=True)
    ])
    assert check_clause_consistency(oc)

    oc = Clause(ClauseType.OR, [
        Literal("1", negated=True, assignment=False), Literal("2", assignment=True)
    ])
    assert check_clause_consistency(oc)

    oc = Clause(ClauseType.OR, [
        Literal("1", negated=True, assignment=False), Literal("2", assignment=False), Literal("3", assignment=False)
    ])
    assert check_clause_consistency(oc)

    oc = Clause(ClauseType.OR, [
        Literal("1", assignment=False), Literal("2", assignment=False), Literal("3", assignment=False)
    ])
    assert check_clause_consistency(oc) == False

    lits = [Literal(str(i), assignment=False) for i in range(100)]
    lits.append(Literal(name="100", negated=True, assignment=False))
    oc = Clause(ClauseType.OR, lits)
    assert check_clause_consistency(oc)

def test_at_most_one_single_literal():
    amo = Clause(ClauseType.AT_MOST_ONE, [
        Literal("1")
    ])
    assert check_clause_consistency(amo) is None

    amo = Clause(ClauseType.AT_MOST_ONE, [
        Literal("1", assignment=True)
    ])
    assert check_clause_consistency(amo)

    amo = Clause(ClauseType.AT_MOST_ONE, [
        Literal("1", assignment=False)
    ])
    assert check_clause_consistency(amo)

def test_at_most_one_multiple_literals():
    amo = Clause(ClauseType.AT_MOST_ONE, [
        Literal("1"), Literal("2", assignment=True), Literal("3")
    ])
    assert check_clause_consistency(amo) is None

    amo = Clause(ClauseType.AT_MOST_ONE, [
        Literal("1", assignment=False), Literal("2", assignment=False), Literal("3", assignment=False)
    ])
    assert check_clause_consistency(amo)

    amo = Clause(ClauseType.AT_MOST_ONE, [
        Literal("1", assignment=False), Literal("2", assignment=False), Literal("3", assignment=True)
    ])
    assert check_clause_consistency(amo)

    amo = Clause(ClauseType.AT_MOST_ONE, [
        Literal("1", assignment=False), Literal("2", assignment=True), Literal("3", assignment=True)
    ])
    assert check_clause_consistency(amo) == False

    amo = Clause(ClauseType.AT_MOST_ONE, [
        Literal("1", assignment=True), Literal("2", assignment=True), Literal("3", assignment=True)
    ])
    assert check_clause_consistency(amo) == False

def test_cnf_single_clause():
    oc = Clause(ClauseType.OR, [
        Literal("1"), Literal("2")
    ])
    cnf = CNF([oc])
    assert check_consistency(cnf) is None

    oc = Clause(ClauseType.OR, [
        Literal("test", assignment=True)
    ])
    cnf = CNF([oc])
    assert check_consistency(cnf)

    oc = Clause(ClauseType.OR, [
        Literal("test", assignment=False)
    ])
    cnf = CNF([oc])
    assert check_consistency(cnf) == False

    oc = Clause(ClauseType.OR, [
        Literal("test", negated=True, assignment=False)
    ])
    cnf = CNF([oc])
    assert check_consistency(cnf)

    oc = Clause(ClauseType.OR, [
        Literal("test", negated=True, assignment=True)
    ])
    cnf = CNF([oc])
    assert check_consistency(cnf) == False

def test_cnf_multiple_clauses():
    cnf = CNF([
        Clause(ClauseType.OR, [
            Literal("1"), Literal("2")
        ]),
        Clause(ClauseType.OR, [
            Literal("2", assignment=True), Literal("3", assignment=True)
        ]),
        Clause(ClauseType.OR, [
            Literal("4", assignment=True), Literal("5", assignment=True)
        ])
    ])
    assert check_consistency(cnf) is None

    cnf = CNF([
        Clause(ClauseType.OR, [
            Literal("1", assignment=True), Literal("2", assignment=True)
        ]),
        Clause(ClauseType.OR, [
            Literal("2", assignment=True), Literal("3", assignment=True)
        ]),
        Clause(ClauseType.OR, [
            Literal("4", assignment=True), Literal("5", assignment=True)
        ])
    ])
    assert check_consistency(cnf)

    cnf = CNF([
        Clause(ClauseType.OR, [
            Literal("1", assignment=False), Literal("2", assignment=False)
        ]),
        Clause(ClauseType.OR, [
            Literal("2", assignment=False), Literal("3", assignment=True)
        ]),
        Clause(ClauseType.OR, [
            Literal("4", assignment=True), Literal("5", assignment=True)
        ])
    ])
    assert check_consistency(cnf) == False

    cnf = CNF([
        Clause(ClauseType.OR, [
            Literal("1"), Literal("2", assignment=True)
        ]),
        Clause(ClauseType.OR, [
            Literal("2", assignment=False), Literal("3", assignment=False)
        ]),
        Clause(ClauseType.OR, [
            Literal("4", assignment=True), Literal("5", assignment=True)
        ])
    ])
    assert check_consistency(cnf) == False
