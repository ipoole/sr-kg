import importlib.util
import sys
from pathlib import Path


def _load_analyzer_module():
    module_path = (
        Path(__file__).resolve().parents[1]
        / "tools"
        / "analyze_fine_grained_graphs.py"
    )
    spec = importlib.util.spec_from_file_location("analyze_fine_grained_graphs", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_parse_worksheet_reads_blocks_roles_and_edges(tmp_path):
    analyzer = _load_analyzer_module()
    worksheet_path = tmp_path / "example.md"
    worksheet_path.write_text(
        """# Example Worksheet

## Fine Blocks

### `x.010.foundation`

Role: `core_claim`

Foundation text.

### `x.020.result`

Role: `derivation_step`

Result text.

## Edge List

| Source | Relation | Target | Note |
| --- | --- | --- | --- |
| `x.020.result` | `derives_from` | `x.010.foundation` | result follows |
""",
        encoding="utf-8",
    )

    worksheet = analyzer.parse_worksheet(worksheet_path)

    assert worksheet.title == "Example Worksheet"
    assert list(worksheet.blocks) == ["x.010.foundation", "x.020.result"]
    assert worksheet.blocks["x.010.foundation"].role == "core_claim"
    assert worksheet.blocks["x.020.result"].draft_order == 20
    assert [(edge.source, edge.relation, edge.target) for edge in worksheet.edges] == [
        ("x.020.result", "derives_from", "x.010.foundation"),
    ]


def test_analysis_orients_dependency_edges_and_ignores_side_links(tmp_path):
    analyzer = _load_analyzer_module()
    worksheet_path = tmp_path / "example.md"
    worksheet_path.write_text(
        """# Example Worksheet

## Fine Blocks

### `x.010.foundation`

Role: `core_claim`

### `x.020.result`

Role: `derivation_step`

### `x.030.support`

Role: `algebra_support`

## Edge List

| Source | Relation | Target | Note |
| --- | --- | --- | --- |
| `x.020.result` | `derives_from` | `x.010.foundation` | result follows |
| `x.030.support` | `supplies_algebra_for` | `x.020.result` | support before result |
| `x.030.support` | `elaborates` | `x.010.foundation` | side link |
""",
        encoding="utf-8",
    )

    analysis = analyzer.analyze_worksheet(analyzer.parse_worksheet(worksheet_path))

    assert analysis.is_dag is True
    assert [
        (constraint.before, constraint.after, constraint.relation)
        for constraint in analysis.constraints
    ] == [
        ("x.010.foundation", "x.020.result", "derives_from"),
        ("x.030.support", "x.020.result", "supplies_algebra_for"),
    ]
    assert [(edge.source, edge.relation, edge.target) for edge in analysis.ignored_edges] == [
        ("x.030.support", "elaborates", "x.010.foundation"),
    ]
    assert analysis.topological_order == (
        "x.010.foundation",
        "x.030.support",
        "x.020.result",
    )
    assert [
        (constraint.before, constraint.after)
        for constraint in analysis.draft_order_conflicts
    ] == [("x.030.support", "x.020.result")]
    assert analysis.optional_role_blocks == ("x.030.support",)


def test_format_analysis_report_includes_cross_experiment_guidance(tmp_path):
    analyzer = _load_analyzer_module()
    worksheet_path = tmp_path / "example.md"
    worksheet_path.write_text(
        """# Example Worksheet

## Fine Blocks

### `x.010.foundation`

Role: `core_claim`

### `x.020.result`

Role: `derivation_step`

## Edge List

| Source | Relation | Target | Note |
| --- | --- | --- | --- |
| `x.020.result` | `requires` | `sr.external` | needs external |
""",
        encoding="utf-8",
    )
    analysis = analyzer.analyze_worksheet(analyzer.parse_worksheet(worksheet_path))

    report = analyzer.format_analysis_report([analysis])

    assert "# Fine-Grained Block Graph Analysis" in report
    assert "`target` must appear before `source`" in report
    assert "`sr.external` _(external)_ -> `x.020.result` _derivation_step_" in report
    assert "Side-link relations" in report
