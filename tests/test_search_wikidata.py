# pyright: strict
from .test_search import verify_search_positive, verify_search_negative

engine = "wikidata"


def test_search_wikidata1():
    verify_search_positive(engine,
                           "TNT",
                           3)


def test_search_wikidata2():
    verify_search_negative(engine,
                           "苹果",
                           5)


def test_search_wikidata3():
    verify_search_positive(engine,
                           "Palytoxin",
                           3)


def test_search_wikidata4():
    verify_search_negative(engine,
                           "(2S,5R,6R)-3,3-dimethyl-7-oxo-6-[(2-phenylacetyl)amino]-4-thia-1-azabicyclo[3.2.0]heptane-2-carboxylic acid",
                           3
                           )
