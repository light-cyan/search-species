# pyright: strict
from .test_search import verify_search_positive, verify_search_negative

engine = "pubchem"


def test_search_pubchem1():
    verify_search_positive(engine, "O-Phenylphenol", 3)


def test_search_pubchem2():
    verify_search_positive(engine, "ABC", 5)


def test_search_pubchem3():
    verify_search_positive(engine, "Palytoxin", 4)


def test_search_pubchem4():
    verify_search_negative(engine, "亚甲基环丙烯", 1)
