#!/usr/bin/env python3
"""
Load and validate queries from JSON configuration file.
"""

import json
import os
from typing import List, Dict


def load_queries(json_path: str = "queries.json") -> List[Dict]:
    """
    Load and validate queries from JSON file.

    Args:
        json_path: Path to the queries JSON file (default: queries.json)

    Returns:
        List of query dictionaries with validated fields

    Raises:
        FileNotFoundError: If the JSON file doesn't exist
        ValueError: If the JSON structure is invalid
    """
    # Load JSON file
    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"Query configuration file not found: {json_path}\n"
            f"Please create it from the template:\n"
            f"  cp queries_template.json queries.json\n"
            f"  # Then edit queries.json with your database details"
        )

    with open(json_path, 'r') as f:
        data = json.load(f)

    if 'queries' not in data:
        raise ValueError("JSON file must contain a 'queries' array")

    queries = data['queries']

    if not isinstance(queries, list) or len(queries) == 0:
        raise ValueError("'queries' must be a non-empty array")

    # Validate and set defaults for each query
    validated_queries = []

    for i, query in enumerate(queries):
        # Required fields
        required_fields = ['name', 'csv_file', 'date_column', 'count_column']
        for field in required_fields:
            if field not in query:
                raise ValueError(
                    f"Query #{i} is missing required field: {field}"
                )

        # Set defaults for optional fields
        validated_query = {
            'name': query['name'],
            'description': query.get('description', query['name']),
            'csv_file': query['csv_file'],
            'date_column': query['date_column'],
            'count_column': query['count_column'],
            'base_query': query.get('base_query'),
            'filtered_query': query.get('filtered_query'),
            'max_date_query': query.get('max_date_query'),
            'order_by': query.get('order_by'),
            'anomaly_threshold_z': query.get('anomaly_threshold_z', -2.5),
            'anomaly_threshold_min': query.get('anomaly_threshold_min', 5000)
        }

        # Ensure CSV parent directory exists
        csv_dir = os.path.dirname(validated_query['csv_file'])
        if csv_dir and not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
            print(f"Created directory: {csv_dir}")

        validated_queries.append(validated_query)

    return validated_queries


def main():
    """Test query loading."""
    try:
        queries = load_queries()
        print(f"Successfully loaded {len(queries)} queries:")
        for query in queries:
            print(f"  - {query['name']}: {query['description']}")
            print(f"    CSV: {query['csv_file']}")
            print(f"    Columns: {query['date_column']}, {query['count_column']}")
            print(f"    Thresholds: z={query['anomaly_threshold_z']}, min={query['anomaly_threshold_min']}")
    except Exception as e:
        print(f"Error loading queries: {e}")
        return 1

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
