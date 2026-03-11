# pyright: strict

from pathlib import Path
import textwrap
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

import warnings
from typing import List, Optional, Tuple

from ._schema import SpeciesCandidate
from ._config import (STRUCT_WIDTH, STRUCT_HEIGHT, CARD_WIDTH, CARD_HEIGHT, DIVIDER_WIDTH,
                      COLUMNS, FONT_SIZE, CHARS_PER_LINE, TEXT_OFFEST_X, TEXT_OFFEST_Y
                      )


def _creatPlaceholderImg() -> Image.Image:
    placeholderImg = Image.new("RGBA", (STRUCT_WIDTH, STRUCT_HEIGHT),
                               "#f5f5f5")
    drawPh = ImageDraw.Draw(placeholderImg)
    bbox = drawPh.textbbox((0, 0), "Image Not Found", font=FONT)
    textWidth = bbox[2] - bbox[0]
    textHeight = bbox[3] - bbox[1]
    x = (STRUCT_WIDTH - textWidth) // 2
    y = (STRUCT_HEIGHT - textHeight) // 2
    drawPh.text((x, y), "Image Not Found", fill="gray", font=FONT)
    return placeholderImg


FONT = ImageFont.truetype("arial.ttf", FONT_SIZE)
PLACEHOLDER_IMG = _creatPlaceholderImg()


def renderCards(jsonFilePaths: List[str],
                outputDir: str
                ) -> Optional[str]:
    cardsData: List[Tuple[SpeciesCandidate, Path]] = []
    for jsonPath in jsonFilePaths:
        try:
            jsonPath = Path(jsonPath)
            if jsonPath.exists():
                new_species = SpeciesCandidate.model_validate_json(
                    jsonPath.read_text(encoding="utf-8")
                )
                dir4json = jsonPath.parent
                cardsData.append((new_species, dir4json))
            else:
                raise FileNotFoundError(jsonPath)

        except Exception as e:
            warnings.warn(f"Skip {jsonPath}\n"  # TODO
                          f"(Reason: {e!r})",
                          UserWarning)

    if not cardsData:
        warnings.warn(f"No valid data loaded.",  # TODO
                      UserWarning)
        return None

    rows = (len(cardsData) + COLUMNS - 1) // COLUMNS
    finalImg = Image.new("RGB", (CARD_WIDTH * COLUMNS, CARD_HEIGHT * rows),
                         "white")
    draw = ImageDraw.Draw(finalImg)

    for idx, (data, fileDir) in enumerate(cardsData):
        x = (idx % COLUMNS) * CARD_WIDTH
        y = (idx // COLUMNS) * CARD_HEIGHT

        img = None
        if data.imgName:
            try:
                imgPath = fileDir / data.imgName
                img = Image.open(imgPath).convert("RGBA")
                origW, origH = img.size
                scale = min(STRUCT_WIDTH / origW, STRUCT_HEIGHT / origH)
                newW, newH = int(origW * scale), int(origH * scale)
                img = img.resize((newW, newH), Image.Resampling.LANCZOS)
            except Exception:
                pass
        if img is None:
            img = PLACEHOLDER_IMG
        px = x + (STRUCT_WIDTH - img.width) // 2
        py = y + (STRUCT_HEIGHT - img.height) // 2
        finalImg.paste(img, (px, py), img if img.mode == "RGBA" else None)

        infoLines = [
            f"---- Candidate {idx} ----",
            f"Source: {data.source}",
            f"Name: {data.name}",
            f"Formula: {data.formula}",
            f"Weight: {data.weight}",
            f"SMILES: {data.smiles}"
        ]
        infoStr = "\n\n".join(textwrap.fill(line, width=CHARS_PER_LINE)
                              for line in infoLines)
        draw.text((x + STRUCT_WIDTH + TEXT_OFFEST_X, y + TEXT_OFFEST_Y),
                  infoStr, fill="black", font=FONT)

        draw.line([(x, y + CARD_HEIGHT - DIVIDER_WIDTH), (x + CARD_WIDTH, y + CARD_HEIGHT - DIVIDER_WIDTH)],
                  fill="#dddddd", width=2)
        if (idx % COLUMNS) < COLUMNS - 1:
            draw.line([(x + CARD_WIDTH - DIVIDER_WIDTH, y), (x + CARD_WIDTH - DIVIDER_WIDTH, y + CARD_HEIGHT)],
                      fill="#dddddd", width=2)

    imgName = f"renderResult_{datetime.now():%Y%m%d%H%M%S}_{len(cardsData)}.png"
    imgPath = Path(outputDir) / imgName
    imgPath.parent.mkdir(parents=True, exist_ok=True)
    finalImg.save(imgPath)
    return str(imgPath)
