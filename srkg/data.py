"""CSV-adjacent data helpers for the SR knowledge graph.

This module owns validation and lightweight normalization of tabular inputs,
plus conversion of node rows into the concept-data mapping used by the injected
viewer. It deliberately does not know about PyVis, HTML generation, physics, or
layout. Callers are responsible for reading the primary CSV files and passing
``pandas`` data frames in.

Dependencies should stay limited to ``srkg.config`` and general-purpose parsing
libraries.
"""

from pathlib import Path
import re

import pandas as pd

from srkg.config import EDGE_COLUMNS, EDGE_KEY_COLUMNS
from srkg.concept_svg_graphics import createSvgGraphic
from srkg.model import Concept, ConceptSection, StudyQuestion

CONTENT_SECTION_COLUMNS = (
    ("definition", "Definition", "definition_new"),
    ("derivation", "Derivation", "derivation_new"),
    ("explanation", "Explanation", "explanation_new"),
)


def build_concept_data(
    nodes_df: pd.DataFrame,
    graphic_designs_df: pd.DataFrame | None = None,
) -> dict[str, dict[str, object]]:
    """Build panel data directly from nodes.csv, independent of PyVis metadata."""
    return {
        concept.id: concept.to_viewer_data()
        for concept in build_concepts(nodes_df, graphic_designs_df)
    }


def build_concepts(
    nodes_df: pd.DataFrame,
    graphic_designs_df: pd.DataFrame | None = None,
) -> list[Concept]:
    """Build internal concept models from source CSV data."""
    concepts = []
    graphic_captions = _graphic_captions_by_id(graphic_designs_df)

    def text(row: pd.Series, *columns: str) -> str:
        for column in columns:
            value = str(row.get(column, "")).strip()
            if value:
                return value
        return ""

    for _, row in nodes_df.iterrows():
        cid = str(row.get("id", "")).strip()
        if not cid:
            continue
        svg_icon = createSvgGraphic(cid, variant="icon")
        svg_detail = createSvgGraphic(cid, variant="detail")
        captions = graphic_captions.get(cid, {})
        concepts.append(Concept(
            id=cid,
            label=str(row.get("label", "")).strip(),
            layer=str(row.get("layer", "")).strip(),
            layer_title=str(row.get("layer_title", "")).strip(),
            sections=[
                ConceptSection(
                    key=key,
                    title=title,
                    text=text(row, column),
                )
                for key, title, column in CONTENT_SECTION_COLUMNS
            ],
            svg_icon=svg_icon or "",
            svg_detail=svg_detail or "",
            svg_icon_caption=captions.get("icon_caption", ""),
            svg_detail_caption=captions.get("detail_caption", ""),
            study_questions=_study_questions(row),
        ))
    return concepts


def _study_questions(row: pd.Series) -> list[StudyQuestion]:
    """Return numbered study question/answer pairs from optional CSV columns."""
    question_numbers = []
    for column in row.index:
        match = re.fullmatch(r"study_question_(\d+)", str(column))
        if match:
            question_numbers.append(int(match.group(1)))

    questions = []
    for number in sorted(question_numbers):
        question = str(row.get(f"study_question_{number}", "")).strip()
        answer = str(row.get(f"study_answer_{number}", "")).strip()
        if question:
            questions.append(StudyQuestion(question=question, answer=answer))
    return questions


def _graphic_captions_by_id(
    graphic_designs_df: pd.DataFrame | None,
) -> dict[str, dict[str, str]]:
    """Return optional SVG caption metadata keyed by concept id."""
    if graphic_designs_df is None or graphic_designs_df.empty:
        return {}

    captions = {}
    for _, row in graphic_designs_df.iterrows():
        cid = str(row.get("id", "")).strip()
        if not cid:
            continue
        captions[cid] = {
            "icon_caption": str(row.get("icon_caption", "")).strip(),
            "detail_caption": str(row.get("detail_caption", "")).strip(),
        }
    return captions


def normalise_edges(edges_df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean the knowledge edge data."""
    missing = set(EDGE_COLUMNS) - set(edges_df.columns)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(f"edges.csv must contain columns: {missing_cols}")

    edges_df = edges_df.copy()
    edges_df["relation"] = edges_df["relation"].replace("", "REFERENCE")

    return edges_df


def validate_edge_endpoints(nodes_df: pd.DataFrame, edges_df: pd.DataFrame) -> None:
    """Raise if any edge endpoint does not refer to a known node id."""
    if "id" not in nodes_df.columns:
        raise ValueError("nodes.csv must contain an 'id' column")

    node_ids = set(nodes_df["id"].astype(str))
    sources = edges_df["source"].astype(str)
    targets = edges_df["target"].astype(str)
    invalid_edges = edges_df[~sources.isin(node_ids) | ~targets.isin(node_ids)]
    if invalid_edges.empty:
        return

    examples = "; ".join(
        f"{row.source}->{row.target}"
        for row in invalid_edges[["source", "target"]].head(5).itertuples(index=False)
    )
    more = "" if len(invalid_edges) <= 5 else f"; ... {len(invalid_edges) - 5} more"
    raise ValueError(
        "edges.csv contains edges with endpoints not present in nodes.csv: "
        f"{examples}{more}"
    )


def parse_bool(value, default: bool = True) -> bool:
    """Parse common CSV boolean spellings."""
    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()
    if text in {"true", "t", "yes", "y", "1"}:
        return True
    if text in {"false", "f", "no", "n", "0"}:
        return False
    return default


def load_edge_key(path: Path | None) -> dict[str, dict[str, str | bool]]:
    """Load relation metadata that controls edge direction and help text."""
    if path is None or not path.exists():
        return {}

    edge_key_df = pd.read_csv(path).fillna("")
    missing = set(EDGE_KEY_COLUMNS) - set(edge_key_df.columns)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(f"{path} must contain columns: {missing_cols}")

    edge_key = {}
    for _, row in edge_key_df.iterrows():
        relation = str(row.get("relation", "")).strip()
        if not relation:
            continue
        edge_key[relation] = {
            "relation": relation,
            "directed": parse_bool(row.get("directed", ""), default=True),
            "category": str(row.get("category", "")).strip(),
            "meaning": str(row.get("meaning", "")).strip(),
            "example": str(row.get("example", "")).strip(),
        }
    return edge_key


def find_edge_key_path(edges_path: Path, configured_path: str | None) -> Path | None:
    """Use an explicit edge key, or edges_key.csv beside the edge file when present."""
    if configured_path:
        path = Path(configured_path)
        if not path.exists():
            raise FileNotFoundError(f"Configured edge key file does not exist: {path}")
        return path

    sibling = edges_path.parent / "edges_key.csv"
    if sibling.exists():
        return sibling

    return None
