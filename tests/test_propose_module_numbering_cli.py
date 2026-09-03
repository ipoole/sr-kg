from tools.propose_module_numbering import build_parser


def test_numbering_parser_accepts_data_root_and_output():
    args = build_parser().parse_args(
        ["--data-root", "example-data", "--out", "proposal.csv", "--apply"]
    )

    assert args.data_root == "example-data"
    assert args.out == "proposal.csv"
    assert args.apply is True
