# pyright: strict

from pathlib import Path
from pydantic import BaseModel, Field, PrivateAttr
from datetime import datetime

from typing import Any, Literal, Optional


class SpeciesCandidate(BaseModel):
    source: Literal["OPSIN", "PubChem", "WikiData"]
    name: str
    formula: Optional[str] = None
    weight: Optional[float] = None
    smiles: Optional[str] = None
    imgName: Optional[str] = None

    imgRes: Optional[bytes] = Field(default=None, exclude=True, repr=False)
    _identifier: str = PrivateAttr()

    @staticmethod
    def cutName(name: str, maxlen: int):
        if len(name) <= maxlen:
            return name
        else:
            return name[:maxlen-3] + "..."

    def model_post_init(self, __context: Any) -> None:
        nameCut = SpeciesCandidate.cutName(self.name, 10)
        self._identifier = f"search{self.source}_{datetime.now():%Y%m%d%H%M%S}_{nameCut}_"

    def save2cache(self, outputDir: Path) -> str:
        outputDir.mkdir(parents=True, exist_ok=True)

        if self.imgRes is not None:
            imgName = self._identifier + ".png"
            imgPath = outputDir / (self._identifier + ".png")
            imgPath.write_bytes(self.imgRes)
            self.imgName = str(imgName)

        fileName = self._identifier + ".json"
        filePath = outputDir / fileName
        filePath.write_text(self.model_dump_json(indent=4), encoding="utf-8")
        return str(fileName)


class SpeciesCandidateAttributeError(Exception):
    def __init__(self, attrName: str, speciesName: str):
        self.attrName = attrName
        self.speciesName = speciesName
        self.message = f"The attribute '{self.attrName}' of species candidate '{self.speciesName}' is None"
        super().__init__(self.message)
