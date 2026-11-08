"""Structural teaching contracts for the first real shared-explanation route."""
from collections import defaultdict
from pathlib import Path

import pytest

from srkg.content_units import ContentExplanation, ContentReference
from srkg.kb import load_knowledge_base

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope='module')
def pilot():
    return load_knowledge_base(ROOT / 'data', domains=['math'], include_graphics=False)


def references(parts):
    for part in parts:
        if isinstance(part, ContentReference):
            yield part
        elif isinstance(part, ContentExplanation):
            yield from references(part.parts)


def test_short_argument_reuses_chart_and_graphic_from_distinct_branches(pilot):
    parents = defaultdict(set)
    for source_id, unit in pilot.content_units.items():
        for ref in references(unit.parts):
            parents[ref.target_id].add(source_id)
    chart = 'math.coordinate_chart.terrain_survey'
    graphic = 'math.tangent_space.graphic'
    assert parents[chart] >= {'math.cotangent_space.basis', 'math.tangent_space.directional_derivative'}
    assert parents[graphic] >= {'math.cotangent_space.terrain_survey', 'math.tangent_space.directional_derivative'}
    assert pilot.content_units[graphic].graphic == 'detail'
    for target in parents:
        assert target in pilot.content_units  # This teaching route is entirely Maths-owned.
        statement = pilot.content_units[target].statement
        assert statement and len(statement.split()) <= 30


def test_the_three_argument_blocks_lead_the_existing_cotangent_page(pilot):
    blocks = pilot.content_blocks_for('math.cotangent_space')
    main = [block.block_id for block in blocks if block.kind != 'overview'][:3]
    assert main == ['math.cotangent_space.gradient_example',
                    'math.cotangent_space.basis', 'math.cotangent_space.terrain_survey']
    assert {'math.cotangent_space.definition', 'math.cotangent_space.units_example',
            'math.cotangent_space.worked_example'} <= {block.block_id for block in blocks}


def test_formal_algebra_and_intuition_stay_separate_with_local_depth(pilot):
    root = pilot.content_units['math.cotangent_space.gradient_example']
    linearity = next(part for part in root.parts
                     if isinstance(part, ContentExplanation) and part.slot == 'linearity')
    assert any(isinstance(part, ContentExplanation) for part in linearity.parts)
    basis = pilot.content_units['math.cotangent_space.basis']
    assert any(isinstance(part, ContentExplanation) and part.slot == 'algebra' for part in basis.parts)
    rate = pilot.content_units['math.cotangent_space.terrain_survey']
    assert any(isinstance(part, ContentExplanation) and part.slot == 'centimetres' for part in rate.parts)
    assert pilot.missing_domains == ('sr',)  # Existing non-pilot prose still refers to SR.
