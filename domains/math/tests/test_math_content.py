from pathlib import Path
import pandas as pd
import re
DOMAIN_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = DOMAIN_ROOT.parents[1] / "data"


def _read_csv(name):
    return pd.read_csv(DOMAIN_ROOT / "data" / name, dtype=str).fillna("")


def test_text_does_not_double_escape_latex_backslashes():
    nodes = _read_csv("nodes.csv")
    concept_ids = set(nodes.loc[nodes["domain"].eq("math"), "id"])
    content_blocks = _read_csv("content_blocks.csv")
    study_questions = _read_csv("study_questions.csv")
    modules = _read_csv("modules.csv")
    module_content_blocks = _read_csv("module_content_blocks.csv")

    content_text = content_blocks.loc[
        content_blocks["concept_id"].isin(concept_ids), ["title", "statement", "body"]
    ]
    question_text = study_questions.loc[
        study_questions["concept_id"].isin(concept_ids), ["prompt", "answer"]
    ]
    module_ids = set(modules.loc[modules["domain"].eq("math"), "module_id"])
    module_text = module_content_blocks.loc[
        module_content_blocks["module_id"].isin(module_ids), ["title", "statement", "body"]
    ]
    # A doubled command/delimiter is an escaping mistake. An aligned-equation
    # row separator followed by whitespace is legitimate TeX, not escaping.
    doubled_latex = r"\\\\(?=[A-Za-z]|\(|\)|\[|\])"
    for text in (content_text, question_text, module_text):
        assert not text.apply(lambda column: column.str.contains(doubled_latex, regex=True)).any().any()


def test_module_titles_include_domain_and_module_number():
    modules = _read_csv("modules.csv")
    modules = modules[modules["domain"].eq("math")]

    expected_prefixes = modules.apply(
        lambda row: f"{'MATHS' if row['domain'] == 'math' else row['domain'].upper()}-"
        f"{int(row['sequence']) // 10} ",
        axis=1,
    )
    assert all(
        title.startswith(prefix)
        for title, prefix in zip(modules["title"], expected_prefixes)
    )
