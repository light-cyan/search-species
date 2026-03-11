## Search Backend Comparison

`search-species` integrates three distinct backends for chemical information retrieval. Each serves a specific purpose in the chemical informatics workflow:

| Feature | **OPSIN** | **PubChem** | **Wikidata** |
| :--- | :--- | :--- | :--- |
| **Core Method** | Algorithmic Parser | Curated Database | Knowledge Graph |
| **Molecular Image** | **Supported** (Rendered) | **Supported** (Stored) | **Rarely Available** |
| **Mass/Formula** | Calculated via **RDKit** | Database Metadata | Database Metadata |
| **Primary Input** | IUPAC English Names | Names, CIDs, SMILES | **Multi-language Names**, IDs |
| **Key Strength** | Handles theoretical molecules. | Highly standardized data. | **Cross-lingual** flexibility. |

---

### 1. OPSIN (Open Parser for Systematic IUPAC Nomenclature)
* **Capabilities**:
    * **Structure Derivation**: Interprets IUPAC names using grammar-based rules rather than searching a fixed list, allowing it to "build" molecules that may not exist in any database.
    * **Real-time Rendering**: Automatically generates a 2D molecular image based on the parsed structure.
    * **RDKit Integration**: Since OPSIN only returns the structure, `search-species` uses **`rdkit.Chem`** to calculate the **Molecular Formula** and **Relative Atomic Mass** from the resulting SMILES.
* **Deficiencies**:
    * **Strict Nomenclature**: Cannot recognize common names or trade names (e.g., it understands `2-acetyloxybenzoic acid` but not `Aspirin`).

### 2. PubChem
* **Capabilities**:
    * **Comprehensive Metadata**: Matches queries against the world's largest free chemical database with high reliability for known substances.
    * **Standardized Images**: Provides professional, high-quality 2D structural diagrams for nearly all entries.
* **Deficiencies**:
    * **Scope Limited to Knowns**: Cannot interpret or generate data for molecules that have not been cataloged in the NCBI registry.

### 3. Wikidata
* **Capabilities**:
    * **Multilingual Search**: Supports queries in various scripts and localized names, making it the most flexible engine for non-English users.
        * *Examples*: `阿司匹林` (Chinese), `アスピリン` (Japanese), `Аспирин` (Russian), `Aspirin` (German).
    * **Character Normalization**: Automatically cleanses chemical formulas by converting Unicode formatting into standard ASCII. This ensures the output is compatible with computational backends like **OpenClaw** or **RDKit**.
        * **Sub/Superscripts**: $₀₁₂₃₄₅₆₇₈₉$ and $⁰¹²³⁴⁵⁶⁷⁸⁹$ $\to$ `0-9`
        * **Charges & Symbols**: $⁺ ⁻ ·$ $\to$ `+ - *`
        * *Example Conversion*: $Fe³⁺$ $\to$ `Fe3+` ; $CuSO₄·5H₂O$ $\to$ `CuSO4*5H2O`
* **Deficiencies**:
    * **Image Scarcity**: Unlike specialized chemical databases, Wikidata entries frequently lack standard molecular diagrams or structural images.
    * **Disabled Cross-Indexing**: Although Wikidata acts as a hub for IDs (CAS, ChemSpider, etc.), cross-database indexing is **not currently enabled** in this tool. It will only return data natively stored in Wikidata.

---

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