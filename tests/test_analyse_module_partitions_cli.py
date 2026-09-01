from tools.analyse_module_partitions import build_parser


def test_partition_parser_accepts_search_controls():
    args = build_parser().parse_args([
        "--data-root",
        "data",
        "--domain",
        "sr",
        "--module-counts",
        "4",
        "5",
        "6",
        "--min-size",
        "5",
        "--max-size",
        "14",
        "--relation-weight",
        "REQUIRES=0.75",
    ])

    assert args.domain == "sr"
    assert args.module_counts == [4, 5, 6]
    assert args.min_size == 5
    assert args.max_size == 14
    assert args.relation_weight == ["REQUIRES=0.75"]


def test_partition_parser_accepts_an_authored_candidate_for_evaluation():
    args = build_parser().parse_args([
        "--domain",
        "sr",
        "--evaluate-members",
        "candidate.csv",
        "--evaluate-only",
        "--show-boundary-edges",
    ])

    assert args.evaluate_members == "candidate.csv"
    assert args.evaluate_only is True
    assert args.show_boundary_edges is True
