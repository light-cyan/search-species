# docs for agent skill are written in ./docs4agentSkill

---

# Engine Backends Reference

## Search Backend Comparison Reference

`search-species` integrates three distinct backends for chemical information retrieval. Each serves a specific purpose in the chemical informatics workflow:

| Feature | **OPSIN** | **PubChem** | **Wikidata** |
| :--- | :--- | :--- | :--- |
| **Core Method** | Algorithmic Parser | Curated Database | Knowledge Graph |
| **Primary Input** | IUPAC English Names | Names, CIDs, SMILES | **Common & Multilingual Names** |
| **Molecular Image** | **Supported** (Rendered) | **Supported** (Stored) | **Rarely Available** |
| **Mass/Formula** | Calculated via **RDKit** | Database Metadata | Database Metadata |
| **Key Strength** | Handles theoretical molecules. | Highly standardized data. | **Vernacular** & Cross-lingual. |


### 1. OPSIN (Open Parser for Systematic IUPAC Nomenclature)
* **Capabilities**:
    * **Structure Derivation**: Interprets IUPAC names using grammar-based rules rather than searching a fixed list, allowing it to "build" molecules that may not exist in any database.
    * **Real-time Rendering**: Automatically generates a 2D molecular image based on the parsed structure.
    * **RDKit Integration**: Since OPSIN only returns the structure, `search-species` uses **`rdkit.Chem`** to calculate the **Molecular Formula** and **Relative Atomic Mass** from the resulting SMILES.
* **Deficiencies**:
    * **Strict Nomenclature Only**: Cannot recognize **Common Names** or trade names. For example, it understands `2-acetyloxybenzoic acid` but will fail on `Aspirin`.

### 2. PubChem
* **Capabilities**:
    * **Established Alias Support**: Successfully matches queries against a massive index of common chemical aliases and trade names known in the industry.
    * **Comprehensive Metadata**: Matches queries against the world's largest free chemical database with high reliability for known substances.
    * **Standardized Images**: Provides professional, high-quality 2D structural diagrams for nearly all entries.
* **Deficiencies**:
    * **Scope Limited to Knowns**: Cannot interpret or generate data for molecules that have not been cataloged in the NCBI registry.

### 3. Wikidata
* **Capabilities**:
    * **Common & Multilingual Names**: As a global knowledge graph, it is the primary engine for **Common Names** and non-English terms. It handles vernacular nomenclature across different scripts with high flexibility.
        * *Examples*: `阿司匹林` (Chinese), `アスピリン` (Japanese), `Аспирин` (Russian), `Aspirin` (German/English).
* **Deficiencies**:
    * **Image Scarcity**: Unlike specialized chemical databases, Wikidata entries frequently lack standard molecular diagrams or structural images.
    * **Disabled Cross-Indexing**: Although Wikidata acts as a hub for IDs (CAS, ChemSpider, etc.), cross-database indexing is **not currently enabled** in this tool. It will only return data natively stored in Wikidata.
* **Data Processing Note (Character Normalization)**:
    * Unlike standard chemical databases, raw Wikidata entries often contain non-standard Unicode formatting. `search-species` automatically cleanses these formulas into standard ASCII. 
    * *Note*: This means the tool's normalized output will look different from a direct web search on Wikidata.
        * **Sub/Superscripts**: $₀₁₂₃₄₅₆₇₈₉$ and $⁰¹²³⁴⁵⁶⁷⁸⁹$ $\to$ `0-9`
        * **Charges & Symbols**: $⁺ ⁻ ·$ $\to$ `+ - *`
        * *Example Conversion*: $Fe³⁺$ $\to$ `Fe3+` ; $CuSO₄·5H₂O$ $\to$ `CuSO4*5H2O`


## Current Scope & Limitations

**⚠️ Important**: `search-species` is focused on core structural identification. The following data points are **NOT** provided:
* ❌ Physical properties (Melting point, Solubility, etc.)
* ❌ Toxicity/Safety data (MSDS)
* ❌ Literature references and Patent links

**Currently Supported Data Fields**:
1.  **Name**: Primary common or systematic name.
2.  **Formula**: Normalized ASCII molecular formula.
3.  **Relative Atomic Mass**: Numerical mass value.
4.  **SMILES**: Canonical structural string.
5.  **Molecular Image**: Visual 2D structure (where available).

---

# Render Module Reference

The `render` module is responsible for taking the structured JSON outputs from the search engines and converting them into a unified, human-readable visual gallery (grid of cards).

## 1. Input Handling & Dependencies
* **JSON-Driven**: The renderer takes paths to `.json` candidate files as its primary input.
* **⚠️ Image Locality (Strict Constraint)**: The module expects the associated 2D structure image to be located in the **exact same directory** as the `.json` file. **Do not move or isolate the JSON files** from their original output directory before rendering. If the image is not found alongside the JSON, the renderer will automatically fallback to an "Image Not Found" placeholder.
* **Fault Tolerance**: Invalid JSON paths or corrupted files are safely skipped with a warning. The rendering process will continue for the remaining valid candidates.

## 2. Card Layout & Grid System
Instead of generating individual image files for each candidate, the module aggregates them into a single comprehensive gallery image.
* **Grid Format**: Cards are arranged in a dynamic multi-column grid. The number of rows scales automatically based on the input count.
* **Card Structure**: Each card has a fixed layout containing:
  * **Left side**: A bounded area for the 2D molecular structure. Original images are proportionally scaled to fit without distortion.
  * **Right side**: A text area displaying the extracted metadata.

## 3. Displayed Data & Constraints
Each card visually displays the following properties:
1. Candidate Index
2. Source Engine (PubChem, OPSIN, or Wikidata)
3. Name
4. Formula
5. Weight (Relative Atomic Mass)
6. SMILES

**⚠️ Important Constraints (Data Truncation):**
To prevent text from breaking the visual layout, strings are strictly managed. Any single property string exceeding the maximum character limit is forcibly truncated. This is highly relevant for **SMILES** strings of large macromolecules, which may not be fully visible on the rendered card. (The complete SMILES is still preserved in the source JSON).

## 4. Output Convention
* **File Naming**: The final merged gallery image is saved using a timestamped format to prevent overwriting previous renders: 
  `renderResult_YYYYMMDDHHMMSS_{number_of_cards}.png`
* **Return Value**: Upon successful execution, the CLI prints the absolute path of the generated gallery image.