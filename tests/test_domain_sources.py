from pathlib import Path
import pandas as pd
import pytest

from srkg.kb import KnowledgeBaseLoadError, load_knowledge_base


COLUMNS = {
    "nodes": ["id", "display_id", "label", "domain", "domain_title"],
    "edges": ["source", "target", "relation", "note"],
    "content_blocks": ["block_id", "concept_id", "sequence", "kind", "title", "body"],
    "study_questions": ["question_id", "concept_id", "sequence", "question_type", "marking_mode", "prompt", "answer"],
    "study_question_options": ["question_id", "option_id", "sequence", "text", "is_correct"],
    "references": ["reference_id", "reference_type", "citation", "authors", "title", "year", "url", "note"],
    "reference_links": ["source_type", "source_id", "reference_id", "locator", "note"],
}


def write_domain(root, domain_id, sequence=0, target=None, body="Definition.", citation=None):
    directory = root / "domains" / domain_id
    directory.mkdir(parents=True)
    (root / "manifest.yaml").write_text("name: Example\ndomains_root: domains\n")
    (directory / "domain.yaml").write_text(f"id: {domain_id}\ntitle: {domain_id}\nsequence: {sequence}\n")
    concept = domain_id + ".alpha"
    records = {
        "nodes": [[concept, domain_id.upper()+"-1.1", domain_id, domain_id, domain_id]],
        "edges": [[concept, target, "REQUIRES", ""]] if target else [],
        "content_blocks": [[concept+".definition", concept, "1", "definition", "Definition", body]],
        "references": [["book", "book", citation, "Author", citation, "2026", "", ""]] if citation else [],
        "reference_links": [["concept", concept, "book", "", ""]] if citation else [],
    }
    for role, columns in COLUMNS.items():
        pd.DataFrame(records.get(role, []), columns=columns).to_csv(directory / (role+".csv"), index=False)
    return directory


def test_domains_are_discovered_without_a_central_registration_list(tmp_path):
    write_domain(tmp_path, "zoology", sequence=1, citation="Zoology book")
    write_domain(tmp_path, "qft", sequence=2, target="zoology.alpha", citation="QFT book")
    kb = load_knowledge_base(tmp_path, include_graphics=False)
    assert [package.id for package in kb.domain_packages] == ["zoology", "qft"]
    assert kb.neighbours("qft.alpha") == ("zoology.alpha",)
    assert kb.concept("zoology.alpha").references[0].citation == "Zoology book"
    assert kb.concept("qft.alpha").references[0].citation == "QFT book"


def test_independent_subset_build_and_unavailable_edge_target(tmp_path):
    write_domain(tmp_path, "molbio")
    directory = write_domain(tmp_path, "optics", target="molbio.alpha")
    kb = load_knowledge_base(tmp_path, domains=["molbio"], include_graphics=False)
    assert list(kb.concept_data()) == ["molbio.alpha"]
    subset=load_knowledge_base(tmp_path, domains=["optics"], include_graphics=False)
    assert subset.edges_df.empty
    assert subset.missing_domains == ("molbio",)
    assert subset.build_warnings[0].kind == "edge"
    assert "edges.csv" in subset.build_warnings[0].location
    assert directory.exists()


def test_unavailable_prose_target_warns_and_preserves_the_authored_body(tmp_path):
    write_domain(tmp_path, "molbio", body=r"Uses \cref{a {nested} label}{other.alpha}.")
    kb=load_knowledge_base(tmp_path, include_graphics=False)
    assert kb.missing_domains == ("other",)
    assert kb.build_warnings[0].kind == "prose-reference"
    assert kb.concepts[0].content_blocks[0].body == r"Uses \cref{a {nested} label}{other.alpha}."


def test_package_cannot_store_another_domains_edge(tmp_path):
    directory = write_domain(tmp_path, "molbio")
    write_domain(tmp_path, "optics")
    pd.DataFrame([["optics.alpha", "molbio.alpha", "REQUIRES", ""]], columns=COLUMNS["edges"]).to_csv(directory/"edges.csv", index=False)
    with pytest.raises(KnowledgeBaseLoadError, match="molbio.*edges.csv.*foreign source"):
        load_knowledge_base(tmp_path, include_graphics=False)


def test_duplicate_global_concept_ids_rejected(tmp_path):
    directory = write_domain(tmp_path, "molbio")
    nodes = pd.read_csv(directory/"nodes.csv")
    pd.concat([nodes, nodes], ignore_index=True).to_csv(directory/"nodes.csv", index=False)
    with pytest.raises(KnowledgeBaseLoadError, match="Duplicate concept"):
        load_knowledge_base(tmp_path, include_graphics=False)


def test_unknown_requested_domain_rejected(tmp_path):
    write_domain(tmp_path, "molbio")
    with pytest.raises(KnowledgeBaseLoadError, match="Unknown domain.*missing"):
        load_knowledge_base(tmp_path, domains=["missing"], include_graphics=False)


def test_future_domain_supplies_graphics_without_shared_registration_changes(tmp_path):
    directory = write_domain(tmp_path, "molbio")
    (directory / "graphics").mkdir()
    (directory / "domain.yaml").write_text((directory / "domain.yaml").read_text()+"graphics: graphics.registry\n")
    (directory / "graphics/motif.py").write_text('def draw(variant):\n    return "<svg>" + variant + "</svg>"\n')
    (directory / "graphics/registry.py").write_text('from .motif import draw\nCONCEPT_CREATORS = {"molbio.alpha": draw}\n')
    kb = load_knowledge_base(tmp_path)
    assert kb.concept("molbio.alpha").svg_icon == "<svg>icon</svg>"
    assert kb.concept("molbio.alpha").svg_detail == "<svg>detail</svg>"


def test_text_only_loading_does_not_import_domain_graphics(tmp_path):
    directory = write_domain(tmp_path, "molbio")
    (directory / "graphics").mkdir()
    (directory / "domain.yaml").write_text((directory / "domain.yaml").read_text()+"graphics: graphics.registry\n")
    (directory / "graphics/registry.py").write_text('raise RuntimeError("provider imported")\n')
    assert load_knowledge_base(tmp_path, include_graphics=False).concepts
    with pytest.raises(KnowledgeBaseLoadError, match="provider imported"):
        load_knowledge_base(tmp_path)


def test_graphics_cannot_register_a_foreign_concept(tmp_path):
    directory = write_domain(tmp_path, "molbio")
    write_domain(tmp_path, "optics")
    (directory / "graphics").mkdir()
    (directory / "domain.yaml").write_text((directory / "domain.yaml").read_text()+"graphics: graphics.registry\n")
    (directory / "graphics/registry.py").write_text('CONCEPT_CREATORS = {"optics.alpha": lambda variant: "<svg/>"}\n')
    with pytest.raises(KnowledgeBaseLoadError, match="molbio.*foreign/unknown IDs.*optics.alpha"):
        load_knowledge_base(tmp_path)


def test_numbering_apply_changes_only_the_explicit_owner(tmp_path):
    from types import SimpleNamespace
    from srkg.domain_sources import owning_source_paths
    from tools.propose_module_numbering import _apply_proposals
    for domain in ("molbio", "optics"):
        directory = write_domain(tmp_path, domain)
        pd.DataFrame([[domain+".m1", domain, domain.upper()+"-1 Foundations", 10, "true"]],
                     columns=["module_id", "domain", "title", "sequence", "default_collapsed"]).to_csv(directory/"modules.csv", index=False)
        pd.DataFrame([[domain+".m1", domain+".alpha", 10]], columns=["module_id", "concept_id", "sequence"]).to_csv(directory/"module_members.csv", index=False)
        pd.DataFrame([[domain+".m1.overview", domain+".m1", 10, "overview", "Overview", "Overview."]],
                     columns=["block_id", "module_id", "sequence", "kind", "title", "body"]).to_csv(directory/"module_content_blocks.csv", index=False)
    other = tmp_path/"domains/optics"
    before = {path: path.read_bytes() for path in other.rglob("*") if path.is_file()}
    with pytest.raises(KnowledgeBaseLoadError, match="--domain"):
        owning_source_paths(tmp_path)
    kb = load_knowledge_base(tmp_path, include_graphics=False)
    _apply_proposals(kb, [SimpleNamespace(concept_id="molbio.alpha", new_display_id="MOLBIO-1.9", member_sequence=20)],
                     paths=owning_source_paths(tmp_path, "molbio"))
    assert pd.read_csv(tmp_path/"domains/molbio/nodes.csv").iloc[0].display_id == "MOLBIO-1.9"
    assert all(path.read_bytes() == content for path, content in before.items())


def test_installing_a_layout_changes_only_its_explicit_domain(tmp_path):
    import json
    from tools.install_layout import install_layout
    first = write_domain(tmp_path, "molbio")
    other = write_domain(tmp_path, "optics")
    (other/"layout.json").write_text(json.dumps({"schema_version": 1, "revision": "7", "concepts": {"optics.alpha": {"x": 5, "y": 6}}, "modules": {}}))
    before = {path: path.read_bytes() for path in other.rglob("*") if path.is_file()}
    exported = tmp_path/"export.json"
    exported.write_text(json.dumps({"schema_version": 1, "revision": "export", "concepts": {"optics.alpha": {"x": 100, "y": 200}, "molbio.alpha": {"x": 10, "y": 20}}, "modules": {}}))
    install_layout(tmp_path, "molbio", exported, "8")
    installed = json.loads((first/"layout.json").read_text())
    assert installed["concepts"] == {"molbio.alpha": {"x": 10, "y": 20}}
    assert installed["revision"] == "8"
    assert all(path.read_bytes() == content for path, content in before.items())


def test_resolved_collection_paths_use_the_same_loader(tmp_path):
    from srkg.kb import load_knowledge_base_from_paths, resolve_knowledge_base_paths
    write_domain(tmp_path, "molbio")
    assert load_knowledge_base_from_paths(resolve_knowledge_base_paths(tmp_path), include_graphics=False).concept("molbio.alpha")


def test_domain_manifest_id_must_match_its_directory(tmp_path):
    write_domain(tmp_path, "molbio")
    second = write_domain(tmp_path, "optics")
    manifest = second/"domain.yaml"
    manifest.write_text(manifest.read_text().replace("id: optics", "id: molbio"))
    with pytest.raises(KnowledgeBaseLoadError, match="manifest.*directory"):
        load_knowledge_base(tmp_path, include_graphics=False)


def test_undirected_edge_duplicates_are_detected_in_either_orientation(tmp_path):
    first = write_domain(tmp_path, "molbio", target="optics.alpha")
    second = write_domain(tmp_path, "optics", target="molbio.alpha")
    for directory in (first, second):
        frame = pd.read_csv(directory/"edges.csv").fillna("")
        frame["relation"] = "RELATED"
        frame.to_csv(directory/"edges.csv", index=False)
    pd.DataFrame([["RELATED", "false", "context", "Related", "Example"]], columns=["relation", "directed", "category", "meaning", "example"]).to_csv(tmp_path/"edges_key.csv", index=False)
    with pytest.raises(KnowledgeBaseLoadError, match="Duplicate domain edge"):
        load_knowledge_base(tmp_path, include_graphics=False)


def test_common_tutorials_are_filtered_individually_and_retained_targets_validate(tmp_path):
    import yaml
    write_domain(tmp_path, "molbio")
    write_domain(tmp_path, "optics")
    routes = [{"tutorial_id": domain+"-tour", "title": "Tour", "category": "interface", "summary": "A tour", "sequence": index,
               "domains": [domain], "steps": [{"step_id": "select", "title": "Select", "commentary": "Read.",
               "action": {"command": "select", "target": "concept:"+domain+".alpha"}}]}
              for index, domain in enumerate(("molbio", "optics"))]
    path=tmp_path/"tutorials.yaml"
    path.write_text(yaml.safe_dump({"schema_version": 1, "tutorials": routes}))
    kb=load_knowledge_base(tmp_path, domains=["molbio"], include_graphics=False)
    assert [route.tutorial_id for route in kb.tutorials] == ["molbio-tour"]
    routes[0]["steps"][0]["action"]["target"] = "concept:optics.alpha"
    path.write_text(yaml.safe_dump({"schema_version": 1, "tutorials": routes}))
    omitted=load_knowledge_base(tmp_path, domains=["molbio"], include_graphics=False)
    assert omitted.tutorials == () and omitted.missing_domains == ("optics",)


def test_initial_selection_must_belong_to_its_declaring_domain(tmp_path):
    first=write_domain(tmp_path, "molbio")
    write_domain(tmp_path, "optics")
    path=first/"domain.yaml"
    path.write_text(path.read_text()+"initial_selection: concept:optics.alpha\n")
    with pytest.raises(KnowledgeBaseLoadError, match="initial_selection.*owned"):
        load_knowledge_base(tmp_path, include_graphics=False)


def test_domain_layout_revision_changes_the_composed_revision(tmp_path):
    import json
    directories=[write_domain(tmp_path, domain) for domain in ("molbio", "optics")]
    (tmp_path/"manifest.yaml").write_text("domains_root: domains\nlayout_revision: '7'\n")
    layout={"schema_version": 1, "revision": "7", "concepts": {}, "modules": {}}
    for directory in directories:(directory/"layout.json").write_text(json.dumps(layout))
    assert load_knowledge_base(tmp_path, include_graphics=False).published_layout.revision == "7"
    (directories[0]/"layout.json").write_text(json.dumps(dict(layout, revision="8")))
    changed=load_knowledge_base(tmp_path, include_graphics=False).published_layout.revision
    assert changed != "7"
    assert changed == load_knowledge_base(tmp_path, include_graphics=False).published_layout.revision


def test_future_domain_owns_its_module_palette(tmp_path):
    import json
    from srkg.kb import resolve_knowledge_base_paths
    from srkg.domain_sources import discover_domains
    from srkg.model import Module
    from srkg.module_colours import build_module_visuals_by_concept
    directory=write_domain(tmp_path,"molbio")
    (directory/"palette.json").write_text(json.dumps([["#abcdef", "#123456"]]))
    path=directory/"domain.yaml"
    path.write_text(path.read_text()+"module_palette: palette.json\n")
    package=discover_domains(resolve_knowledge_base_paths(tmp_path))[0]
    visuals=build_module_visuals_by_concept([Module("molbio.m1", "molbio", "BIO-1", 10, members=["molbio.alpha"])], palettes={package.id:package.palette})
    assert visuals["molbio.alpha"]["background"] == "#abcdef"
    assert visuals["molbio.alpha"]["border"] == "#123456"


@pytest.mark.parametrize("role,column", [("nodes", "id"), ("content_blocks", "block_id")])
def test_owned_record_ids_must_use_the_package_namespace(tmp_path, role, column):
    directory = write_domain(tmp_path, "molbio")
    path = directory/(role+".csv")
    frame = pd.read_csv(path).fillna("")
    frame.loc[0, column] = "other.example"
    frame.to_csv(path, index=False)
    with pytest.raises(KnowledgeBaseLoadError, match="namespace.*molbio"):
        load_knowledge_base(tmp_path, include_graphics=False)


def test_selected_domain_does_not_read_any_unselected_package_file(tmp_path, monkeypatch):
    import builtins
    from srkg.domain_sources import read_authored_table, owning_source_paths
    write_domain(tmp_path, "molbio")
    other=write_domain(tmp_path, "optics")
    (other/"domain.yaml").write_text("This manifest is deliberately broken")
    original_path_open, original_open = Path.open, builtins.open
    def guard(path):
        if isinstance(path, (str, Path)) and Path(path).resolve().is_relative_to(other.resolve()):
            raise AssertionError(f"Read unselected package: {path}")
    def path_open(path, *args, **kwargs):
        guard(path)
        return original_path_open(path, *args, **kwargs)
    def builtin_open(path, *args, **kwargs):
        guard(path)
        return original_open(path, *args, **kwargs)
    monkeypatch.setattr(Path, "open", path_open)
    monkeypatch.setattr(builtins, "open", builtin_open)
    kb=load_knowledge_base(tmp_path, domains=["molbio"])
    assert list(kb.concept_data()) == ["molbio.alpha"]
    assert list(read_authored_table(tmp_path, "nodes", domain="molbio")["id"]) == ["molbio.alpha"]
    assert owning_source_paths(tmp_path, "molbio").root.name == "molbio"


@pytest.mark.parametrize("body,target", [("Definition.", "molbio.typo"), (r"Uses \cref{missing}{molbio.typo}.", None)])
def test_missing_targets_in_a_loaded_namespace_still_fail(tmp_path, body, target):
    write_domain(tmp_path,"molbio",body=body,target=target)
    with pytest.raises(KnowledgeBaseLoadError, match="molbio.typo.*loaded domain"):
        load_knowledge_base(tmp_path,include_graphics=False)


def test_external_typo_is_not_checked_until_its_namespace_is_loaded(tmp_path):
    write_domain(tmp_path,"molbio",target="optics.typo")
    write_domain(tmp_path,"optics")
    subset=load_knowledge_base(tmp_path,domains=["molbio"],include_graphics=False)
    assert subset.missing_domains == ("optics",)
    with pytest.raises(KnowledgeBaseLoadError, match="optics.typo.*loaded domain"):
        load_knowledge_base(tmp_path,include_graphics=False)


def add_module(directory, domain):
    pd.DataFrame([[domain+".m1",domain,domain.upper()+"-1 Foundations",10,"true"]], columns=["module_id","domain","title","sequence","default_collapsed"]).to_csv(directory/"modules.csv",index=False)
    pd.DataFrame([[domain+".m1",domain+".alpha",10]],columns=["module_id","concept_id","sequence"]).to_csv(directory/"module_members.csv",index=False)
    pd.DataFrame([[domain+".m1.overview",domain+".m1",10,"overview","Overview","An overview."]],columns=["block_id","module_id","sequence","kind","title","body"]).to_csv(directory/"module_content_blocks.csv",index=False)


@pytest.mark.parametrize("target_type,target", [("concept","other.alpha"),("module","other.m1")])
def test_unavailable_support_is_omitted_without_removing_its_module(tmp_path,target_type,target):
    directory=write_domain(tmp_path,"molbio")
    add_module(directory,"molbio")
    pd.DataFrame([["molbio.m1",target_type,target,"prerequisite",""]], columns=["module_id","target_type","target_id","role","note"]).to_csv(directory/"module_supports.csv",index=False)
    kb=load_knowledge_base(tmp_path,include_graphics=False)
    assert len(kb.modules) == 1 and kb.modules[0].members == ["molbio.alpha"]
    assert kb.modules[0].supports == []
    assert kb.missing_domains == ("other",)
    assert kb.build_warnings[0].kind == "module-support"


def test_invalid_support_type_is_not_hidden_by_an_unloaded_target(tmp_path):
    directory=write_domain(tmp_path,"molbio")
    add_module(directory,"molbio")
    pd.DataFrame([["molbio.m1","bogus","other.alpha","prerequisite",""]],columns=["module_id","target_type","target_id","role","note"]).to_csv(directory/"module_supports.csv",index=False)
    with pytest.raises(KnowledgeBaseLoadError,match="invalid target_type"):
        load_knowledge_base(tmp_path,include_graphics=False)


def test_subject_tutorial_missing_requirements_are_warned_and_omitted(tmp_path):
    import yaml
    directory=write_domain(tmp_path,"molbio")
    routes=[{"tutorial_id":"local-tour","title":"Local","category":"physics","summary":"Read", "sequence":1,"domains":["molbio"],
             "steps":[{"step_id":"one","title":"Select","commentary":"Read", "action":{"command":"select","target":"concept:molbio.alpha"}}]},
            {"tutorial_id":"external-tour","title":"External","category":"physics","summary":"Read","sequence":2,"domains":["molbio","optics"],
             "steps":[{"step_id":"one","title":"Select","commentary":"Read", "action":{"command":"select","target":"concept:optics.alpha"}}]}]
    (directory/"tutorials.yaml").write_text(yaml.safe_dump({"schema_version":1,"tutorials":routes}))
    kb=load_knowledge_base(tmp_path,include_graphics=False)
    assert [route.tutorial_id for route in kb.tutorials] == ["local-tour"]
    assert kb.missing_domains == ("optics",)
    assert any(warning.kind=="tutorial" and warning.source=="external-tour" for warning in kb.build_warnings)


def test_subject_tutorial_external_pointer_is_omitted_even_if_not_declared(tmp_path):
    import yaml
    directory=write_domain(tmp_path,"molbio")
    route={"tutorial_id":"pointer-tour","title":"Pointer","category":"physics","summary":"Read","sequence":1,"domains":["molbio"],
           "steps":[{"step_id":"one","title":"Read","commentary":"Read", "action":{"command":"wait","milliseconds":0},
                     "pointer":{"target":"details:block:optics.alpha.definition"}}]}
    (directory/"tutorials.yaml").write_text(yaml.safe_dump({"schema_version":1,"tutorials":[route]}))
    kb=load_knowledge_base(tmp_path,include_graphics=False)
    assert kb.tutorials == () and kb.missing_domains == ("optics",)


def test_unavailable_subject_route_does_not_hide_a_loaded_namespace_typo(tmp_path):
    import yaml
    directory=write_domain(tmp_path,"molbio")
    route={"tutorial_id":"broken-tour","title":"Broken","category":"physics","summary":"Read","sequence":1,"domains":["molbio","optics"],
           "steps":[{"step_id":"one","title":"Read","commentary":"Read", "action":{"command":"select","target":"concept:molbio.typo"}}]}
    (directory/"tutorials.yaml").write_text(yaml.safe_dump({"schema_version":1,"tutorials":[route]}))
    with pytest.raises(KnowledgeBaseLoadError,match="molbio.typo"):
        load_knowledge_base(tmp_path,include_graphics=False)


@pytest.mark.parametrize("mode", ["generate", "--validate-only", "--dag-report-only", "--module-report-only", "--validate"])
def test_generator_modes_use_only_selected_sources_and_report_external_warnings(tmp_path, capsys, mode):
    from tools.generate_pyvis import main
    directory=write_domain(tmp_path,"molbio",target="optics.typo",body=r"Uses \cref{outside}{optics.typo}.")
    other=write_domain(tmp_path,"optics")
    (other/"domain.yaml").write_text("This excluded manifest cannot be parsed")
    nodes=pd.read_csv(directory/"nodes.csv")
    nodes.loc[len(nodes)] = ["molbio.beta","MOLBIO-1.2","Second","molbio","molbio"]
    nodes.to_csv(directory/"nodes.csv",index=False)
    blocks=pd.read_csv(directory/"content_blocks.csv")
    blocks.loc[len(blocks)] = ["molbio.beta.definition","molbio.beta",2,"definition","Definition","Second definition."]
    blocks.to_csv(directory/"content_blocks.csv",index=False)
    edges=pd.read_csv(directory/"edges.csv").fillna("")
    edges.loc[len(edges)] = ["molbio.alpha","molbio.beta","REQUIRES",""]
    edges.to_csv(directory/"edges.csv",index=False)
    add_module(directory,"molbio")
    members=pd.read_csv(directory/"module_members.csv")
    members.loc[len(members)] = ["molbio.m1","molbio.beta",20]
    members.to_csv(directory/"module_members.csv",index=False)
    output=tmp_path/"viewer.html"
    args=["--data-root",str(tmp_path),"--domains","molbio","--out",str(output)]
    if mode != "generate":
        args.append(mode)
    main(args)
    captured=capsys.readouterr()
    assert "optics" in captured.err and "edges.csv" in captured.err
    assert captured.err.count("Warning:") == 1
    assert output.exists() == (mode in {"generate","--validate"})
    if output.exists():
        assert captured.out.splitlines()[-1] == "Missing domains: optics"


def test_warning_report_groups_domains_and_counts_a_route_once():
    from srkg.domain_references import BuildWarning, format_build_warnings
    warnings=[BuildWarning("tutorial","optics","optics.one","route.step1","tour"),
              BuildWarning("tutorial","optics","optics.two","route.step2","tour"),
              BuildWarning("edge","optics","optics.one","edges.csv row 2"),
              BuildWarning("edge","optics","optics.two","edges.csv row 3")]
    report=format_build_warnings(warnings)
    assert "optics" in report and "2 omitted edges" in report and "1 omitted tutorial" in report
    assert "route.step1" in report
    assert format_build_warnings(()) == ""


@pytest.mark.parametrize("fault", ["csv", "palette", "graphics"])
def test_faulty_unselected_data_or_graphics_do_not_affect_an_independent_build(tmp_path, fault):
    write_domain(tmp_path,"molbio")
    other=write_domain(tmp_path,"optics")
    manifest=other/"domain.yaml"
    if fault == "csv":
        (other/"edges.csv").write_text("broken\nvalue\n")
    elif fault == "palette":
        manifest.write_text(manifest.read_text()+"module_palette: palette.json\n")
        (other/"palette.json").write_text("not json")
    else:
        manifest.write_text(manifest.read_text()+"graphics: graphics.registry\n")
        (other/"graphics").mkdir()
        (other/"graphics/registry.py").write_text('raise RuntimeError("broken excluded provider")\n')
    assert load_knowledge_base(tmp_path,domains=["molbio"]).missing_domains == ()
    with pytest.raises(KnowledgeBaseLoadError):
        load_knowledge_base(tmp_path,domains=["optics"])


def test_shared_content_loads_across_domains_without_changing_edges(tmp_path):
    math = write_domain(tmp_path, 'math', body=r'\explain{source}{sr.alpha.definition}{SR definition}{Why?}')
    sr = write_domain(tmp_path, 'sr')
    frame = pd.read_csv(sr / 'content_blocks.csv')
    frame['statement'] = 'A short borrowed result.'
    frame.to_csv(sr / 'content_blocks.csv', index=False)
    kb = load_knowledge_base(tmp_path, include_graphics=False)
    assert kb.edges_df.empty  # A scoped explanation is not a new concept dependency.
    assert len(kb.content_units) == 2
    assert kb.content_units['math.alpha.definition'].statement == ''
    assert kb.concept('math.alpha').content_blocks[0].statement == ''  # No NaN from mixed columns.
    assert kb.content_units['sr.alpha.definition'].statement == 'A short borrowed result.'
    assert kb.content_unit_data()['math.alpha.definition']['parts'][0]['target_id'] == 'sr.alpha.definition'
    # Explicit subset loading must not even open the other domain's manifest.
    (sr / 'domain.yaml').write_text('deliberately unreadable: [broken')
    subset = load_knowledge_base(tmp_path, domains=['math'], include_graphics=False)
    assert set(subset.content_units) == {'math.alpha.definition'}
    assert subset.missing_domains == ('sr',)
    assert subset.build_warnings[0].kind == 'content-reference'
    ref = subset.content_units['math.alpha.definition'].parts[0]
    assert subset.content_units.resolve(ref).state == 'unavailable'
    assert ref.target_label == 'SR definition'


def test_loaded_domain_missing_block_is_an_error_even_if_concept_exists(tmp_path):
    write_domain(tmp_path, 'math', body=r'\explain{missing}{sr.alpha.typo}{SR result}{Why?}')
    write_domain(tmp_path, 'sr')
    with pytest.raises(KnowledgeBaseLoadError, match='sr.alpha.typo.*unresolved'):
        load_knowledge_base(tmp_path, include_graphics=False)


def test_new_optional_fields_and_named_children_reach_the_common_model(tmp_path):
    directory = write_domain(tmp_path, 'math', body=r'\explanation{why}{Why?}{Local maths: \(x^2\).}')
    frame = pd.read_csv(directory / 'content_blocks.csv')
    frame['statement'] = r'\(x\) is a coordinate.'
    frame['graphic'] = ''
    frame.to_csv(directory / 'content_blocks.csv', index=False)
    kb = load_knowledge_base(tmp_path, include_graphics=False)
    block = kb.concepts[0].content_blocks[0]
    unit = kb.content_units[block.block_id]
    assert unit.source_id == block.block_id  # Notes/read marks retain their native source ID.
    assert unit.statement == block.statement
    assert unit.parts[0].slot == 'why'
    assert unit.parts[0].parts[0].text == r'Local maths: \(x^2\).'


def test_statement_concept_references_obey_selected_domain_policy(tmp_path):
    directory = write_domain(tmp_path, 'math')
    frame = pd.read_csv(directory / 'content_blocks.csv')
    frame['statement'] = r'Uses \cref{SR}{sr.alpha}.'
    frame.to_csv(directory / 'content_blocks.csv', index=False)
    subset = load_knowledge_base(tmp_path, domains=['math'], include_graphics=False)
    assert subset.missing_domains == ('sr',)
    assert subset.build_warnings[0].kind == 'prose-reference'
    assert subset.content_units['math.alpha.definition'].statement == frame.loc[0, 'statement']
