# pyright: strict

from pathlib import Path
from urllib.parse import quote
import requests
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors

from typing import List, Tuple, no_type_check, Optional
import warnings

from .._config import ERR_MSG_MAX_LEN
from .._schema import SpeciesCandidate


baseUrl = "https://opsin.ch.cam.ac.uk/opsin"


class OpsinRequestError(requests.RequestException):
    pass


@no_type_check  # opsin does not support querying weight and formula
def getPropertiesFromSmiles(smiles: Optional[str]
                            ) -> Tuple[Optional[str], Optional[float]]:
    if smiles is None:
        return None, None

    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            formula = rdMolDescriptors.CalcMolFormula(mol)
            weight = rdMolDescriptors.CalcExactMolWt(mol)
            return formula, weight

    except Exception as e:
        warnings.warn(f""  # TODO
                      f"(Reason: {e!r})",
                      UserWarning)
        return None, None


def fetchSMILES(safeQuery: str
                ) -> Optional[str]:
    smiles: Optional[str] = None
    try:
        response = requests.get(baseUrl + f"/{safeQuery}" + ".json",
                                timeout=10)
        try:
            data = response.json()
            if not response.ok or data.get("status") != "SUCCESS":
                raise OpsinRequestError(str(data)[:ERR_MSG_MAX_LEN])
            smiles = data.get("smiles")

        except requests.exceptions.JSONDecodeError:
            response.raise_for_status()

    except requests.RequestException as e:
        warnings.warn(f""  # TODO
                      f"(Reason: {e!r})",
                      UserWarning)

    return smiles


def fetchImage(safeQuery: str
               ) -> Optional[bytes]:
    imgRes: Optional[bytes] = None
    try:
        response = requests.get(baseUrl + f"/{safeQuery}" + ".png",
                                timeout=10)
        if not response.ok or not response.content:
            raise OpsinRequestError(response.text[:ERR_MSG_MAX_LEN]
                                    if response.text
                                    else f"HTTP {response.status_code} Response content is empty.")
        imgRes = response.content

    except requests.RequestException as e:
        warnings.warn(f""  # TODO
                      f"(Reason: {e!r})",
                      UserWarning)

    return imgRes


def search(query: str,
           outputDir: str
           ) -> List[Tuple[SpeciesCandidate, str]]:
    safeQuery = quote(query)

    smiles = fetchSMILES(safeQuery)

    formula, weight = getPropertiesFromSmiles(smiles)

    imgRes = fetchImage(safeQuery)

    if any(x is not None for x in [smiles, imgRes, formula, weight]):
        specData = SpeciesCandidate(
            source="OPSIN",
            name=query,
            formula=formula,
            weight=weight,
            smiles=smiles,
            imgRes=imgRes
        )
        resultPath = specData.save2cache(Path(outputDir))
        return [(specData, resultPath)]
    else:
        return []
