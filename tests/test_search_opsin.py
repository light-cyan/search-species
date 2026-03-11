# pyright: strict
from .test_search import verify_search_positive, verify_search_negative

engine = "opsin"


def test_search_opsin1():
    verify_search_positive(engine,
                           "(2S,5R,6R)-3,3-dimethyl-7-oxo-6-[(2-phenylacetyl)amino]-4-thia-1-azabicyclo[3.2.0]heptane-2-carboxylic acid",
                           1
                           )


def test_search_opsin2():
    verify_search_negative(engine, "ABC", 1)


def test_search_opsin3():
    verify_search_negative(engine, "邻苯二酚",  1)


def test_search_opsin4():
    verify_search_positive(engine, "Methylene cyclopropene", 1)
