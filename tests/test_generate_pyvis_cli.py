from tools.generate_pyvis import build_parser


def test_generate_pyvis_parser_accepts_module_report_options():
    args = build_parser().parse_args([
        "--data-root",
        "data",
        "--module-report-only",
        "--module-relations",
        "DERIVES_FROM",
        "REQUIRES",
    ])

    assert args.module_report_only is True
    assert args.module_relations == ["DERIVES_FROM", "REQUIRES"]


def test_generate_pyvis_parser_accepts_viewer_relation_filter():
    args = build_parser().parse_args([
        "--relations",
        "REQUIRES",
        "DERIVES_FROM",
        "CONSTRUCTED_FROM",
    ])

    assert args.relations == ["REQUIRES", "DERIVES_FROM", "CONSTRUCTED_FROM"]
