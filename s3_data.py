"""
Data store for S3 data, it resides in it's own file for readability 
"""

data = {
    "standard": {"price_per_gb": 0.023},
    "standard_ia": {
        "price_per_gb": 0.0125,
        "transition_cost": 0.01,
        "items_per_transition_chunk": 1000,
        "data_retrieval_cost_per_gb": 0.01,
    },
    "standard_ia_one_zone": {
        "price_per_gb": 0.01,
        "transition_cost": 0.01,
        "items_per_transition_chunk": 1000,
        "data_retrieval_cost_per_gb": 0.01,
    },
    "glacier": {
        "price_per_gb": 0.004,
        "transition_cost": 0.05,
        "items_per_transition_chunk": 1000,
        "data_retrieval_cost_per_gb": 0.01,
    },
    "glacier_deep_archive": {
        "price_per_gb": 0.00099,
        "transition_cost": 0.05,
        "items_per_transition_chunk": 1000,
        "data_retrieval_cost_per_gb": 0.02,
    },
}
