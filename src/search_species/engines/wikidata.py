# pyright: strict

from pathlib import Path
import requests
from urllib.parse import quote

import warnings
from typing import List, Tuple, Optional, TypedDict

from .._config import ERR_MSG_MAX_LEN, CONTENT__USER_AGENT
from .._schema import SpeciesCandidate


searchUrl = "https://www.wikidata.org/w/api.php"
sparqlUrl = "https://query.wikidata.org/sparql"
baseImgUrl = "https://commons.wikimedia.org/wiki/Special:FilePath"


class WikidataRequestError(requests.RequestException):
    pass


def fetchCandidates(query: str
                    ) -> List[str]:
    candidateList: List[str] = []
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "format": "json",
        "type": "item"
    }
    try:
        response = requests.get(searchUrl, params=params,
                                headers={"User-Agent": CONTENT__USER_AGENT},
                                timeout=10)

        try:
            candidateData = response.json()

            if not candidateData.get("search", []):
                raise WikidataRequestError(
                    str(candidateData)[:ERR_MSG_MAX_LEN]
                )

            candidateList = [item["id"] for item in candidateData["search"]]

        except requests.exceptions.JSONDecodeError:
            response.raise_for_status()

    except requests.RequestException as e:
        warnings.warn(f""  # TODO
                      f"(Reason: {e!r})",
                      UserWarning)

    return candidateList


class SpeciesProperty(TypedDict):
    qid: str
    name:  Optional[str]
    formula: Optional[str]
    weight: Optional[float]
    smiles: Optional[str]
    imgUrl: Optional[str]


transMap = str.maketrans(
    "₀₁₂₃₄₅₆₇₈₉⁺⁻⁰¹²³⁴⁵⁶⁷⁸⁹·",
    "0123456789+-0123456789*"
)


def fetchProperty(qid: str
                  ) -> List[SpeciesProperty]:
    speciesProperties: List[SpeciesProperty] = []

    # P233: Canonical SMILES, P2067: Mass, P18: Image, P274: Formula
    query = f"""
    SELECT ?label ?formula ?mass ?smiles ?image WHERE {{
      BIND(wd:{qid} AS ?compound)
      FILTER EXISTS {{
        {{ ?compound wdt:P233 ?anyS. }} UNION
        {{ ?compound wdt:P2017 ?anyIS. }} UNION
        {{ ?compound wdt:P274 ?anyF. }} UNION
        {{ ?compound wdt:P231 ?anyCAS. }}
      }}
      OPTIONAL {{ ?compound wdt:P274 ?formula. }}
      OPTIONAL {{ ?compound wdt:P2067 ?mass. }}
      OPTIONAL {{ ?compound wdt:P233 ?smiles. }}
      OPTIONAL {{ ?compound wdt:P18 ?image. }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". ?compound rdfs:label ?label. }}
    }}
    """

    try:
        response = requests.get(sparqlUrl, params={'query': query, 'format': 'json'},
                                headers={"User-Agent": CONTENT__USER_AGENT},
                                timeout=10)

        try:
            propData = response.json()
            if "results" not in propData:
                raise WikidataRequestError(str(propData)[:ERR_MSG_MAX_LEN])
            properties = propData.get("results", {})\
                .get("bindings", [])

            for prop in properties:
                name = prop.get("label", {}).get("value", None)
                formula = prop.get("formula", {}).get("value", None)
                if type(formula) is str:  # Console defaults to GBK encoding
                    formula = formula.translate(transMap)
                weight = float(prop.get("mass", {}).get("value", None)
                               or 0) or None
                smiles = prop.get("smiles", {}).get("value", None)
                imgProp = prop.get("image", {}).get("value", None)
                imgUrl = None
                if type(imgProp) is str:
                    if imgProp.startswith("http:"):
                        imgUrl = "https:" + imgProp.removeprefix("http:")
                    elif imgProp.startswith("https:"):
                        imgUrl = imgProp
                    else:
                        imgUrl = baseImgUrl + quote(imgProp)
                speciesProperties.append(
                    SpeciesProperty(
                        qid=qid,
                        name=name,
                        formula=formula,
                        weight=weight,
                        smiles=smiles,
                        imgUrl=imgUrl
                    )
                )

        except (requests.exceptions.JSONDecodeError, ValueError):
            response.raise_for_status()

    except requests.RequestException as e:
        warnings.warn(f""  # TODO
                      f"(Reason: {e!r})",
                      UserWarning)

    return speciesProperties


def fetchImage(imgUrl: Optional[str]
               ) -> Optional[bytes]:
    imgRes: Optional[bytes] = None
    if not imgUrl:
        return imgRes
    try:
        response = requests.get(imgUrl, headers={"User-Agent": CONTENT__USER_AGENT},
                                timeout=10)

        if not response.ok or not response.content:
            raise WikidataRequestError(response.text[:ERR_MSG_MAX_LEN]
                                       if response.text
                                       else f"HTTP {response.status_code} Response content is empty.")

        imgRes = response.content

    except requests.RequestException as e:
        warnings.warn(f""  # TODO
                      f"(Reason: {e!r})",
                      UserWarning)

    return imgRes


def search(query: str,
           maxCandidates: int,
           outputDir: str
           ) -> List[Tuple[SpeciesCandidate, str]]:

    candidateQIDs = fetchCandidates(query)

    resultDatas: List[Tuple[SpeciesCandidate, str]] = []

    for qid in candidateQIDs[:maxCandidates]:
        properties = fetchProperty(qid)

        for prop in properties:

            imgRes = fetchImage(prop["imgUrl"])
            specData = SpeciesCandidate(
                source="WikiData",
                name=prop["name"] or "Name Not Found",
                formula=prop["formula"],
                weight=prop["weight"],
                smiles=prop["smiles"],
                imgRes=imgRes
            )

            resultDatas.append((specData,
                                specData.save2cache(Path(outputDir))))

    return resultDatas
