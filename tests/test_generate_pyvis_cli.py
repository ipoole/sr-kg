from tools.generate_pyvis import build_parser


def test_generate_pyvis_parser_defaults_to_product_title():
    args = build_parser().parse_args([])

    assert args.title == ["PhysicsKG - An Atlas of Physics Knowledge"]
    assert args.out == "PhysicsKG.html"


def test_generate_pyvis_parser_defaults_to_physicskg_google_drive_client(monkeypatch):
    monkeypatch.delenv("PHYSICSKG_GOOGLE_DRIVE_CLIENT_ID", raising=False)

    args = build_parser().parse_args([])

    assert args.google_drive_client_id == (
        "45956259452-4sd6v6vmi653bqfs5vfdcsn2bab85ea8.apps.googleusercontent.com"
    )


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
