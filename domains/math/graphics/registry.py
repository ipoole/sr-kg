"""Graphic registration owned by this domain."""
from .concepts import (
    create_m_1_1_manifold,
    create_m_1_2_coordinate_chart,
    create_m_1_3_coordinate_transformation,
    create_m_1_4_worldline,
    create_m_1_5_tangent_space,
    create_m_1_6_cotangent_space,
    create_m_2_1_tensor_field,
    create_m_2_2_index_notation,
    create_m_2_3_tensor_transformation_law,
)
from .modules import MODULE_CREATORS

CONCEPT_CREATORS = {
    'math.manifold': create_m_1_1_manifold,
    'math.coordinate_chart': create_m_1_2_coordinate_chart,
    'math.coordinate_transformation': create_m_1_3_coordinate_transformation,
    'math.worldline': create_m_1_4_worldline,
    'math.tangent_space': create_m_1_5_tangent_space,
    'math.cotangent_space': create_m_1_6_cotangent_space,
    'math.tensor_field': create_m_2_1_tensor_field,
    'math.index_notation': create_m_2_2_index_notation,
    'math.tensor_transformation_law': create_m_2_3_tensor_transformation_law,
}
