# pyright: strict

from pathlib import Path
from urllib.parse import quote
import requests

import warnings
from typing import List, Tuple, Optional, TypedDict

from .._config import ERR_MSG_MAX_LEN
from .._schema import SpeciesCandidate


baseUrl = "https://pubchem.ncbi.nlm.nih.gov/rest"


class PubchemRequestError(requests.RequestException):
    pass


def fetchCandidates(safeQuery: str
                    ) -> List[str]:
    candidateList: List[str] = []
    try:
        response = requests.get(baseUrl + f"/autocomplete/compound/{safeQuery}/json",
                                timeout=10)

        try:
            candidateData = response.json()

            if candidateData.get("total", 0) == 0:
                raise PubchemRequestError(
                    str(candidateData)[:ERR_MSG_MAX_LEN]
                )

            candidateList = candidateData.get("dictionary_terms", {})\
                .get("compound", [])

        except requests.exceptions.JSONDecodeError:
            response.raise_for_status()

    except requests.RequestException as e:
        warnings.warn(f""  # TODO
                      f"(Reason: {e!r})",
                      UserWarning)

    return candidateList


class SpeciesProperty(TypedDict):
    cid: Optional[int]
    name: str
    formula: Optional[str]
    weight: Optional[float]
    smiles: Optional[str]


def fetchProperty(species: str
                  ) -> List[SpeciesProperty]:
    speciesProperties: List[SpeciesProperty] = []
    try:
        response = requests.get(baseUrl + f"/pug/compound/name/{species}/property/Title,MolecularFormula,MolecularWeight,IsomericSMILES/json",
                                timeout=10)
        try:
            propData = response.json()
            if "PropertyTable" not in propData:
                raise PubchemRequestError(str(propData)[:ERR_MSG_MAX_LEN])
            properties = propData.get("PropertyTable", {})\
                .get("Properties", [])

            for prop in properties:
                name = prop.get("Title", species)
                formula = prop.get("MolecularFormula", None)
                weight = prop.get("MolecularWeight", None)
                smiles = prop.get("SMILES", None)
                cid = prop.get("CID")
                speciesProperties.append(
                    SpeciesProperty(cid=cid,
                                    name=name,
                                    formula=formula,
                                    weight=weight,
                                    smiles=smiles
                                    ))

        except requests.exceptions.JSONDecodeError:
            response.raise_for_status()

    except requests.RequestException as e:
        warnings.warn(f""  # TODO
                      f"(Reason: {e!r})",
                      UserWarning)

    return speciesProperties


def fetchImage(cid: Optional[int]
               ) -> Optional[bytes]:
    imgRes: Optional[bytes] = None

    if cid is None:
        return imgRes

    try:
        response = requests.get(baseUrl + f"/pug/compound/cid/{cid}/png",
                                timeout=10)

        if not response.ok or not response.content:
            raise PubchemRequestError(response.text[:ERR_MSG_MAX_LEN]
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
    safeQuery = quote(query)

    candidateList = fetchCandidates(safeQuery)

    resultDatas: List[Tuple[SpeciesCandidate, str]] = []
    for species in candidateList[:maxCandidates]:

        properties = fetchProperty(species)
        for prop in properties:

            imgRes = fetchImage(prop["cid"])
            specData = SpeciesCandidate(
                source="PubChem",
                name=prop["name"],
                formula=prop["formula"],
                weight=prop["weight"],
                smiles=prop["smiles"],
                imgRes=imgRes
            )

            resultDatas.append((specData,
                                specData.save2cache(Path(outputDir))))

    return resultDatas
