# pyright: strict
import argparse
from typing import List, Tuple, cast


def search_cli() -> None:
    from ._schema import SpeciesCandidate
    from .engines import opsin, pubchem, wikidata

    parser = argparse.ArgumentParser(
        description="Search chemical species via multiple engines"
    )
    parser.add_argument("engine", choices=["pubchem", "opsin", "wikidata", "all"], metavar="ENGINE",
                        help="Search engine to use")
    parser.add_argument("query", type=str, metavar="NAME",
                        help="Chemical name or query string")
    parser.add_argument("max_cands", type=int, nargs='?', default=3, metavar="INT",
                        help="Maximum search results (ignored by OPSIN, default: 3)")
    parser.add_argument("-o", "--output_dir", type=str, default="./cache", metavar="DIR",
                        help="Output directory (default: ./cache)")
    args = parser.parse_args()

    output_dir = args.output_dir

    results: List[Tuple[SpeciesCandidate, str]] = []

    if args.engine in ["pubchem", "all"]:
        results.extend(pubchem.search(args.query, args.max_cands, output_dir))

    if args.engine in ["opsin", "all"]:
        results.extend(opsin.search(args.query, output_dir))

    if args.engine in ["wikidata", "all"]:
        results.extend(wikidata.search(args.query, args.max_cands, output_dir))

    if not results:
        print("No search results")
    else:
        for spec, path in results:
            print(f"SpeciesCandidate({spec}) written -> {path}")


def render_cli() -> None:
    from .renderCard import renderCards

    parser = argparse.ArgumentParser(
        description="Render species candidate cards"
    )
    parser.add_argument("candidate_files", nargs="+", metavar="JSON",
                        help="JSON files of species records")
    parser.add_argument("-o", "--output_dir", type=str, default="./gallery", metavar="DIR",
                        help="Output directory for images (default: ./gallery)")
    args = parser.parse_args()

    output_dir = args.output_dir

    cardPath = renderCards(cast(List[str], args.candidate_files), output_dir)
    if cardPath:
        print(f"Successfully rendered -> {cardPath}")
