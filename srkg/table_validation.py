"""Fail-fast relational contracts for loaded authored tables.

These checks raise KnowledgeBaseLoadError; editorial diagnostics remain in
validation.py. They operate on frames and do not read files or construct SVGs.
"""

import pandas as pd

from srkg.schema import (
    CONTENT_BLOCK_COLUMNS,
    CONTENT_BLOCK_KINDS,
    STUDY_QUESTION_COLUMNS,
    STUDY_QUESTION_TYPES,
    STUDY_QUESTION_MARKING_MODES,
    STUDY_QUESTION_OPTION_COLUMNS,
    REFERENCE_COLUMNS,
    REFERENCE_LINK_COLUMNS,
    REFERENCE_LINK_SOURCE_TYPES,
    MODULE_COLUMNS,
    MODULE_MEMBER_COLUMNS,
    MODULE_SUPPORT_COLUMNS,
    MODULE_SUPPORT_TARGET_TYPES,
    MODULE_CONTENT_BLOCK_COLUMNS,
    MODULE_GRAPHIC_DESIGN_COLUMNS,
    KnowledgeBaseLoadError,
)


def validate_unique_concept_ids(nodes_df: pd.DataFrame) -> None:
    if "id" not in nodes_df.columns:
        raise KnowledgeBaseLoadError("nodes.csv must contain an 'id' column")
    ids = nodes_df["id"].astype(str).str.strip()
    duplicates = sorted(id_ for id_ in ids[ids.duplicated()].unique() if id_)
    if duplicates:
        raise KnowledgeBaseLoadError(
            "Duplicate concept id(s) in nodes.csv: " + ", ".join(duplicates)
        )


def validate_display_ids(nodes_df: pd.DataFrame) -> None:
    if "display_id" not in nodes_df.columns:
        raise KnowledgeBaseLoadError("nodes.csv must contain a 'display_id' column")

    display_ids = nodes_df["display_id"].astype(str).str.strip()
    if display_ids.eq("").any():
        raise KnowledgeBaseLoadError("nodes.csv has empty display_id value(s)")

    duplicates = sorted(id_ for id_ in display_ids[display_ids.duplicated()].unique() if id_)
    if duplicates:
        raise KnowledgeBaseLoadError(
            "Duplicate display_id value(s) in nodes.csv: " + ", ".join(duplicates)
        )


def validate_content_blocks(
    nodes_df: pd.DataFrame,
    content_blocks_df: pd.DataFrame | None,
) -> None:
    if content_blocks_df is None or content_blocks_df.empty:
        if content_blocks_df is not None:
            raise KnowledgeBaseLoadError("content_blocks.csv must contain at least one row")
        return

    missing = set(CONTENT_BLOCK_COLUMNS) - set(content_blocks_df.columns)
    if missing:
        raise KnowledgeBaseLoadError(
            "content_blocks.csv is missing columns: " + ", ".join(sorted(missing))
        )

    block_ids = content_blocks_df["block_id"].astype(str).str.strip()
    duplicate_block_ids = sorted(id_ for id_ in block_ids[block_ids.duplicated()].unique() if id_)
    if duplicate_block_ids:
        raise KnowledgeBaseLoadError(
            "Duplicate content block id(s) in content_blocks.csv: "
            + ", ".join(duplicate_block_ids)
        )

    for column in ("block_id", "concept_id", "sequence", "kind", "title", "body"):
        values = content_blocks_df[column].astype(str).str.strip()
        if values.eq("").any():
            raise KnowledgeBaseLoadError(f"content_blocks.csv has empty {column} value(s)")

    sequence_values = content_blocks_df["sequence"].astype(str).str.strip()
    non_numeric_sequences = sorted(
        value for value in sequence_values.unique() if not _is_integer(value)
    )
    if non_numeric_sequences:
        raise KnowledgeBaseLoadError(
            "content_blocks.csv has non-numeric sequence value(s): "
            + ", ".join(non_numeric_sequences)
        )

    kinds = content_blocks_df["kind"].astype(str).str.strip()
    invalid_kinds = sorted(kind for kind in kinds.unique() if kind not in CONTENT_BLOCK_KINDS)
    if invalid_kinds:
        raise KnowledgeBaseLoadError(
            "content_blocks.csv has invalid kind value(s): "
            + ", ".join(invalid_kinds)
        )

    concept_ids = set(nodes_df["id"].astype(str).str.strip())
    block_concept_ids = content_blocks_df["concept_id"].astype(str).str.strip()
    unknown_ids = sorted(id_ for id_ in block_concept_ids.unique() if id_ and id_ not in concept_ids)
    if unknown_ids:
        raise KnowledgeBaseLoadError(
            "content_blocks.csv references unknown concept id(s): "
            + ", ".join(unknown_ids)
        )

    concepts_without_blocks = sorted(
        concept_id for concept_id in concept_ids if concept_id and concept_id not in set(block_concept_ids)
    )
    if concepts_without_blocks:
        raise KnowledgeBaseLoadError(
            "content_blocks.csv has no blocks for concept id(s): "
            + ", ".join(concepts_without_blocks)
        )


def validate_study_questions(
    nodes_df: pd.DataFrame,
    study_questions_df: pd.DataFrame | None,
    study_question_options_df: pd.DataFrame | None,
) -> None:
    if study_questions_df is None:
        return

    missing = set(STUDY_QUESTION_COLUMNS) - set(study_questions_df.columns)
    if missing:
        raise KnowledgeBaseLoadError(
            "study_questions.csv is missing columns: " + ", ".join(sorted(missing))
        )

    question_ids = study_questions_df["question_id"].astype(str).str.strip()
    duplicate_question_ids = sorted(
        id_ for id_ in question_ids[question_ids.duplicated()].unique() if id_
    )
    if duplicate_question_ids:
        raise KnowledgeBaseLoadError(
            "Duplicate study question id(s) in study_questions.csv: "
            + ", ".join(duplicate_question_ids)
        )

    for column in (
        "question_id",
        "concept_id",
        "sequence",
        "question_type",
        "marking_mode",
        "prompt",
    ):
        values = study_questions_df[column].astype(str).str.strip()
        if values.eq("").any():
            raise KnowledgeBaseLoadError(f"study_questions.csv has empty {column} value(s)")

    sequence_values = study_questions_df["sequence"].astype(str).str.strip()
    non_numeric_sequences = sorted(
        value for value in sequence_values.unique() if not _is_integer(value)
    )
    if non_numeric_sequences:
        raise KnowledgeBaseLoadError(
            "study_questions.csv has non-numeric sequence value(s): "
            + ", ".join(non_numeric_sequences)
        )

    question_types = study_questions_df["question_type"].astype(str).str.strip()
    invalid_question_types = sorted(
        question_type
        for question_type in question_types.unique()
        if question_type not in STUDY_QUESTION_TYPES
    )
    if invalid_question_types:
        raise KnowledgeBaseLoadError(
            "study_questions.csv has invalid question_type value(s): "
            + ", ".join(invalid_question_types)
        )

    marking_modes = study_questions_df["marking_mode"].astype(str).str.strip()
    invalid_marking_modes = sorted(
        marking_mode
        for marking_mode in marking_modes.unique()
        if marking_mode not in STUDY_QUESTION_MARKING_MODES
    )
    if invalid_marking_modes:
        raise KnowledgeBaseLoadError(
            "study_questions.csv has invalid marking_mode value(s): "
            + ", ".join(invalid_marking_modes)
        )

    concept_ids = set(nodes_df["id"].astype(str).str.strip())
    question_concept_ids = study_questions_df["concept_id"].astype(str).str.strip()
    unknown_ids = sorted(
        id_ for id_ in question_concept_ids.unique() if id_ and id_ not in concept_ids
    )
    if unknown_ids:
        raise KnowledgeBaseLoadError(
            "study_questions.csv references unknown concept id(s): "
            + ", ".join(unknown_ids)
        )

    if study_question_options_df is None:
        return

    missing_option_columns = (
        set(STUDY_QUESTION_OPTION_COLUMNS) - set(study_question_options_df.columns)
    )
    if missing_option_columns:
        raise KnowledgeBaseLoadError(
            "study_question_options.csv is missing columns: "
            + ", ".join(sorted(missing_option_columns))
        )

    for column in STUDY_QUESTION_OPTION_COLUMNS:
        values = study_question_options_df[column].astype(str).str.strip()
        if values.eq("").any():
            raise KnowledgeBaseLoadError(
                f"study_question_options.csv has empty {column} value(s)"
            )

    option_ids = study_question_options_df["option_id"].astype(str).str.strip()
    duplicate_option_ids = sorted(
        option_id
        for option_id in option_ids[option_ids.duplicated()].unique()
        if option_id
    )
    if duplicate_option_ids:
        raise KnowledgeBaseLoadError(
            "Duplicate study question option id(s) in study_question_options.csv: "
            + ", ".join(duplicate_option_ids)
        )

    option_sequences = study_question_options_df["sequence"].astype(str).str.strip()
    non_numeric_option_sequences = sorted(
        value for value in option_sequences.unique() if not _is_integer(value)
    )
    if non_numeric_option_sequences:
        raise KnowledgeBaseLoadError(
            "study_question_options.csv has non-numeric sequence value(s): "
            + ", ".join(non_numeric_option_sequences)
        )

    correct_values = (
        study_question_options_df["is_correct"].astype(str).str.strip().str.lower()
    )
    invalid_correct_values = sorted(
        value for value in correct_values.unique() if value not in {"true", "false"}
    )
    if invalid_correct_values:
        raise KnowledgeBaseLoadError(
            "study_question_options.csv has invalid is_correct value(s): "
            + ", ".join(invalid_correct_values)
        )

    known_question_ids = set(question_ids)
    option_question_ids = (
        study_question_options_df["question_id"].astype(str).str.strip()
    )
    unknown_question_ids = sorted(set(option_question_ids) - known_question_ids)
    if unknown_question_ids:
        raise KnowledgeBaseLoadError(
            "study_question_options.csv references unknown question id(s): "
            + ", ".join(unknown_question_ids)
        )

    options_by_question = {
        question_id: study_question_options_df[option_question_ids.eq(question_id)]
        for question_id in known_question_ids
    }
    mode_by_question = dict(zip(question_ids, marking_modes, strict=True))
    for question_id in sorted(known_question_ids):
        options = options_by_question[question_id]
        marking_mode = mode_by_question[question_id]
        if marking_mode == "self_assessed" and not options.empty:
            raise KnowledgeBaseLoadError(
                f"Self-assessed study question {question_id} must not have options"
            )
        if marking_mode != "automatic":
            continue
        if len(options) < 2:
            raise KnowledgeBaseLoadError(
                f"Automatic study question {question_id} must have at least two options"
            )
        correct_count = (
            options["is_correct"].astype(str).str.strip().str.lower().eq("true").sum()
        )
        if correct_count != 1:
            raise KnowledgeBaseLoadError(
                f"Automatic study question {question_id} must have exactly one correct option"
            )


def validate_references(references_df: pd.DataFrame | None) -> None:
    if references_df is None:
        return

    missing = set(REFERENCE_COLUMNS) - set(references_df.columns)
    if missing:
        raise KnowledgeBaseLoadError(
            "references.csv is missing columns: " + ", ".join(sorted(missing))
        )

    if references_df.empty:
        return

    reference_ids = references_df["reference_id"].astype(str).str.strip()
    duplicate_reference_ids = sorted(
        id_ for id_ in reference_ids[reference_ids.duplicated()].unique() if id_
    )
    if duplicate_reference_ids:
        raise KnowledgeBaseLoadError(
            "Duplicate reference id(s) in references.csv: "
            + ", ".join(duplicate_reference_ids)
        )

    for column in ("reference_id", "reference_type", "citation", "title"):
        values = references_df[column].astype(str).str.strip()
        if values.eq("").any():
            raise KnowledgeBaseLoadError(f"references.csv has empty {column} value(s)")


def validate_reference_links(
    nodes_df: pd.DataFrame,
    content_blocks_df: pd.DataFrame | None,
    study_questions_df: pd.DataFrame | None,
    references_df: pd.DataFrame | None,
    reference_links_df: pd.DataFrame | None,
) -> None:
    if reference_links_df is None:
        return

    missing = set(REFERENCE_LINK_COLUMNS) - set(reference_links_df.columns)
    if missing:
        raise KnowledgeBaseLoadError(
            "reference_links.csv is missing columns: " + ", ".join(sorted(missing))
        )

    if reference_links_df.empty:
        return

    for column in ("source_type", "source_id", "reference_id"):
        values = reference_links_df[column].astype(str).str.strip()
        if values.eq("").any():
            raise KnowledgeBaseLoadError(f"reference_links.csv has empty {column} value(s)")

    source_types = reference_links_df["source_type"].astype(str).str.strip()
    invalid_source_types = sorted(
        source_type
        for source_type in source_types.unique()
        if source_type not in REFERENCE_LINK_SOURCE_TYPES
    )
    if invalid_source_types:
        raise KnowledgeBaseLoadError(
            "reference_links.csv has invalid source_type value(s): "
            + ", ".join(invalid_source_types)
        )

    reference_ids = (
        set(references_df["reference_id"].astype(str).str.strip())
        if references_df is not None and "reference_id" in references_df.columns
        else set()
    )
    linked_reference_ids = reference_links_df["reference_id"].astype(str).str.strip()
    unknown_reference_ids = sorted(
        id_ for id_ in linked_reference_ids.unique() if id_ and id_ not in reference_ids
    )
    if unknown_reference_ids:
        raise KnowledgeBaseLoadError(
            "reference_links.csv references unknown reference id(s): "
            + ", ".join(unknown_reference_ids)
        )

    concept_ids = set(nodes_df["id"].astype(str).str.strip())
    content_block_ids = (
        set(content_blocks_df["block_id"].astype(str).str.strip())
        if content_blocks_df is not None and "block_id" in content_blocks_df.columns
        else set()
    )
    study_question_ids = (
        set(study_questions_df["question_id"].astype(str).str.strip())
        if study_questions_df is not None and "question_id" in study_questions_df.columns
        else set()
    )
    known_sources = {
        "concept": concept_ids,
        "content_block": content_block_ids,
        "study_question": study_question_ids,
    }
    unknown_sources = []
    for row in reference_links_df.itertuples(index=False):
        source_type = str(getattr(row, "source_type")).strip()
        source_id = str(getattr(row, "source_id")).strip()
        if source_id and source_id not in known_sources.get(source_type, set()):
            unknown_sources.append(f"{source_type}:{source_id}")

    if unknown_sources:
        raise KnowledgeBaseLoadError(
            "reference_links.csv references unknown source id(s): "
            + ", ".join(sorted(set(unknown_sources)))
        )


def validate_module_graphic_designs(
    modules_df: pd.DataFrame | None,
    designs_df: pd.DataFrame | None,
) -> None:
    """Validate optional module graphics without requiring every module to have one."""
    if designs_df is None:
        return
    missing = set(MODULE_GRAPHIC_DESIGN_COLUMNS) - set(designs_df.columns)
    if missing:
        raise KnowledgeBaseLoadError(
            "module_graphic_designs.csv is missing columns: " + ", ".join(sorted(missing))
        )
    ids = designs_df["module_id"].astype(str).str.strip()
    if ids.eq("").any():
        raise KnowledgeBaseLoadError("module_graphic_designs.csv has empty module_id value(s)")
    duplicates = sorted(ids[ids.duplicated()].unique())
    if duplicates:
        raise KnowledgeBaseLoadError(
            "Duplicate module graphic id(s): " + ", ".join(duplicates)
        )
    known = (
        set(modules_df["module_id"].astype(str).str.strip())
        if modules_df is not None else set()
    )
    unknown = sorted(set(ids) - known)
    if unknown:
        raise KnowledgeBaseLoadError(
            "module_graphic_designs.csv references unknown module id(s): "
            + ", ".join(unknown)
        )


def validate_modules(
    nodes_df: pd.DataFrame,
    modules_df: pd.DataFrame | None,
    module_members_df: pd.DataFrame | None,
    module_supports_df: pd.DataFrame | None,
    module_content_blocks_df: pd.DataFrame | None,
) -> None:
    module_sources = [
        modules_df,
        module_members_df,
        module_supports_df,
        module_content_blocks_df,
    ]
    if all(df is None for df in module_sources):
        return

    if modules_df is None:
        raise KnowledgeBaseLoadError("modules.csv is required when module files are present")
    if module_members_df is None:
        raise KnowledgeBaseLoadError(
            "module_members.csv is required when modules.csv is present"
        )
    if module_content_blocks_df is None:
        raise KnowledgeBaseLoadError(
            "module_content_blocks.csv is required when modules.csv is present"
        )

    validate_modules_df(nodes_df, modules_df)
    validate_module_members(nodes_df, modules_df, module_members_df)
    validate_module_supports(nodes_df, modules_df, module_supports_df)
    validate_module_content_blocks(modules_df, module_content_blocks_df)


def validate_modules_df(nodes_df: pd.DataFrame, modules_df: pd.DataFrame) -> None:
    missing = set(MODULE_COLUMNS) - set(modules_df.columns)
    if missing:
        raise KnowledgeBaseLoadError(
            "modules.csv is missing columns: " + ", ".join(sorted(missing))
        )

    module_ids = modules_df["module_id"].astype(str).str.strip()
    duplicate_module_ids = sorted(
        id_ for id_ in module_ids[module_ids.duplicated()].unique() if id_
    )
    if duplicate_module_ids:
        raise KnowledgeBaseLoadError(
            "Duplicate module id(s) in modules.csv: " + ", ".join(duplicate_module_ids)
        )

    for column in ("module_id", "domain", "title", "sequence"):
        values = modules_df[column].astype(str).str.strip()
        if values.eq("").any():
            raise KnowledgeBaseLoadError(f"modules.csv has empty {column} value(s)")

    sequence_values = modules_df["sequence"].astype(str).str.strip()
    non_numeric_sequences = sorted(
        value for value in sequence_values.unique() if not _is_integer(value)
    )
    if non_numeric_sequences:
        raise KnowledgeBaseLoadError(
            "modules.csv has non-numeric sequence value(s): "
            + ", ".join(non_numeric_sequences)
        )

    known_domains = _node_domains(nodes_df)
    module_domains = modules_df["domain"].astype(str).str.strip()
    unknown_domains = sorted(
        domain
        for domain in module_domains.unique()
        if domain and known_domains and domain not in known_domains
    )
    if unknown_domains:
        raise KnowledgeBaseLoadError(
            "modules.csv references unknown domain(s): " + ", ".join(unknown_domains)
        )


def validate_module_members(
    nodes_df: pd.DataFrame,
    modules_df: pd.DataFrame,
    module_members_df: pd.DataFrame,
) -> None:
    missing = set(MODULE_MEMBER_COLUMNS) - set(module_members_df.columns)
    if missing:
        raise KnowledgeBaseLoadError(
            "module_members.csv is missing columns: " + ", ".join(sorted(missing))
        )

    if module_members_df.empty:
        raise KnowledgeBaseLoadError("module_members.csv must contain at least one row")

    for column in ("module_id", "concept_id", "sequence"):
        values = module_members_df[column].astype(str).str.strip()
        if values.eq("").any():
            raise KnowledgeBaseLoadError(
                f"module_members.csv has empty {column} value(s)"
            )

    sequence_values = module_members_df["sequence"].astype(str).str.strip()
    non_numeric_sequences = sorted(
        value for value in sequence_values.unique() if not _is_integer(value)
    )
    if non_numeric_sequences:
        raise KnowledgeBaseLoadError(
            "module_members.csv has non-numeric sequence value(s): "
            + ", ".join(non_numeric_sequences)
        )

    module_ids = set(modules_df["module_id"].astype(str).str.strip())
    concept_ids = set(nodes_df["id"].astype(str).str.strip())
    member_module_ids = module_members_df["module_id"].astype(str).str.strip()
    member_concept_ids = module_members_df["concept_id"].astype(str).str.strip()

    unknown_modules = sorted(
        id_ for id_ in member_module_ids.unique() if id_ and id_ not in module_ids
    )
    if unknown_modules:
        raise KnowledgeBaseLoadError(
            "module_members.csv references unknown module id(s): "
            + ", ".join(unknown_modules)
        )

    unknown_concepts = sorted(
        id_ for id_ in member_concept_ids.unique() if id_ and id_ not in concept_ids
    )
    if unknown_concepts:
        raise KnowledgeBaseLoadError(
            "module_members.csv references unknown concept id(s): "
            + ", ".join(unknown_concepts)
        )

    duplicate_concepts = sorted(
        id_ for id_ in member_concept_ids[member_concept_ids.duplicated()].unique() if id_
    )
    if duplicate_concepts:
        raise KnowledgeBaseLoadError(
            "module_members.csv assigns concept(s) to multiple modules: "
            + ", ".join(duplicate_concepts)
        )

    concepts_without_module = sorted(concept_ids - set(member_concept_ids))
    if concepts_without_module:
        raise KnowledgeBaseLoadError(
            "module_members.csv has no module for concept id(s): "
            + ", ".join(concepts_without_module)
        )

    module_domain_by_id = {
        str(row.module_id).strip(): str(row.domain).strip()
        for row in modules_df.itertuples(index=False)
    }
    concept_domain_by_id = _node_domain_by_id(nodes_df)
    cross_domain_memberships = []
    for row in module_members_df.itertuples(index=False):
        module_id = str(row.module_id).strip()
        concept_id = str(row.concept_id).strip()
        module_domain = module_domain_by_id.get(module_id, "")
        concept_domain = concept_domain_by_id.get(concept_id, "")
        if module_domain and concept_domain and module_domain != concept_domain:
            cross_domain_memberships.append(f"{concept_id} -> {module_id}")

    if cross_domain_memberships:
        raise KnowledgeBaseLoadError(
            "module_members.csv assigns concept(s) to modules in a different domain: "
            + ", ".join(sorted(set(cross_domain_memberships)))
        )


def validate_module_supports(
    nodes_df: pd.DataFrame,
    modules_df: pd.DataFrame,
    module_supports_df: pd.DataFrame | None,
) -> None:
    if module_supports_df is None:
        return

    missing = set(MODULE_SUPPORT_COLUMNS) - set(module_supports_df.columns)
    if missing:
        raise KnowledgeBaseLoadError(
            "module_supports.csv is missing columns: " + ", ".join(sorted(missing))
        )

    if module_supports_df.empty:
        return

    for column in ("module_id", "target_type", "target_id", "role"):
        values = module_supports_df[column].astype(str).str.strip()
        if values.eq("").any():
            raise KnowledgeBaseLoadError(
                f"module_supports.csv has empty {column} value(s)"
            )

    target_types = module_supports_df["target_type"].astype(str).str.strip()
    invalid_target_types = sorted(
        target_type
        for target_type in target_types.unique()
        if target_type not in MODULE_SUPPORT_TARGET_TYPES
    )
    if invalid_target_types:
        raise KnowledgeBaseLoadError(
            "module_supports.csv has invalid target_type value(s): "
            + ", ".join(invalid_target_types)
        )

    module_ids = set(modules_df["module_id"].astype(str).str.strip())
    concept_ids = set(nodes_df["id"].astype(str).str.strip())
    support_module_ids = module_supports_df["module_id"].astype(str).str.strip()
    unknown_modules = sorted(
        id_ for id_ in support_module_ids.unique() if id_ and id_ not in module_ids
    )
    if unknown_modules:
        raise KnowledgeBaseLoadError(
            "module_supports.csv references unknown module id(s): "
            + ", ".join(unknown_modules)
        )

    known_targets = {
        "concept": concept_ids,
        "module": module_ids,
    }
    unknown_targets = []
    for row in module_supports_df.itertuples(index=False):
        target_type = str(row.target_type).strip()
        target_id = str(row.target_id).strip()
        if target_id and target_id not in known_targets.get(target_type, set()):
            unknown_targets.append(f"{target_type}:{target_id}")

    if unknown_targets:
        raise KnowledgeBaseLoadError(
            "module_supports.csv references unknown target id(s): "
            + ", ".join(sorted(set(unknown_targets)))
        )


def validate_module_content_blocks(
    modules_df: pd.DataFrame,
    module_content_blocks_df: pd.DataFrame,
) -> None:
    missing = set(MODULE_CONTENT_BLOCK_COLUMNS) - set(module_content_blocks_df.columns)
    if missing:
        raise KnowledgeBaseLoadError(
            "module_content_blocks.csv is missing columns: "
            + ", ".join(sorted(missing))
        )

    if module_content_blocks_df.empty:
        raise KnowledgeBaseLoadError(
            "module_content_blocks.csv must contain at least one row"
        )

    for column in ("block_id", "module_id", "sequence", "kind", "title", "body"):
        values = module_content_blocks_df[column].astype(str).str.strip()
        if values.eq("").any():
            raise KnowledgeBaseLoadError(
                f"module_content_blocks.csv has empty {column} value(s)"
            )

    block_ids = module_content_blocks_df["block_id"].astype(str).str.strip()
    duplicate_block_ids = sorted(
        id_ for id_ in block_ids[block_ids.duplicated()].unique() if id_
    )
    if duplicate_block_ids:
        raise KnowledgeBaseLoadError(
            "Duplicate module content block id(s) in module_content_blocks.csv: "
            + ", ".join(duplicate_block_ids)
        )

    sequence_values = module_content_blocks_df["sequence"].astype(str).str.strip()
    non_numeric_sequences = sorted(
        value for value in sequence_values.unique() if not _is_integer(value)
    )
    if non_numeric_sequences:
        raise KnowledgeBaseLoadError(
            "module_content_blocks.csv has non-numeric sequence value(s): "
            + ", ".join(non_numeric_sequences)
        )

    kinds = module_content_blocks_df["kind"].astype(str).str.strip()
    invalid_kinds = sorted(kind for kind in kinds.unique() if kind not in CONTENT_BLOCK_KINDS)
    if invalid_kinds:
        raise KnowledgeBaseLoadError(
            "module_content_blocks.csv has invalid kind value(s): "
            + ", ".join(invalid_kinds)
        )

    module_ids = set(modules_df["module_id"].astype(str).str.strip())
    block_module_ids = module_content_blocks_df["module_id"].astype(str).str.strip()
    unknown_modules = sorted(
        id_ for id_ in block_module_ids.unique() if id_ and id_ not in module_ids
    )
    if unknown_modules:
        raise KnowledgeBaseLoadError(
            "module_content_blocks.csv references unknown module id(s): "
            + ", ".join(unknown_modules)
        )

    modules_without_blocks = sorted(module_ids - set(block_module_ids))
    if modules_without_blocks:
        raise KnowledgeBaseLoadError(
            "module_content_blocks.csv has no blocks for module id(s): "
            + ", ".join(modules_without_blocks)
        )


def _node_domain_by_id(nodes_df: pd.DataFrame) -> dict[str, str]:
    domains = {}
    for row in nodes_df.itertuples(index=False):
        concept_id = str(getattr(row, "id")).strip()
        domain = str(getattr(row, "domain", "") or "").strip()
        if not domain and "." in concept_id:
            domain = concept_id.split(".", 1)[0]
        domains[concept_id] = domain
    return domains


def _node_domains(nodes_df: pd.DataFrame) -> set[str]:
    return {domain for domain in _node_domain_by_id(nodes_df).values() if domain}


def _is_integer(value: str) -> bool:
    try:
        int(value)
    except ValueError:
        return False
    return True


