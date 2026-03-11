from .test_search import verify_search_positive, verify_search_negative


def test_search_pubchem1():
    verify_search_positive("pubchem", "O-Phenylphenol", 3)


def test_search_pubchem2():
    verify_search_positive("pubchem", "ABC", 1)


def test_search_pubchem3():
    verify_search_negative("pubchem", "亚甲基环丙烯", 1)
