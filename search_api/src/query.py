import json
from typing import Any, Dict, List

ELASTICSEARCH_INDEX = "chatbot"


class QueryCreator:
    def __init__(self):
        self.config = {}

    def create_query(
        self,
        entities: Dict[str, Any],
        top_k: int,
    ) -> Dict[str, Any]:
        """Create optimized query in Elasticsearch

        Args:
            entities (Dict[str, Any]): Entities from user's message
            top_k (int): Number of results to return

        Returns:
            Dict[str, Any]: Elasticsearch query configuration
        """
        # Validate required fields
        if "dish_names" not in entities:
            entities["dish_names"] = []
        if isinstance(entities["dish_names"], str):
            entities["dish_names"] = [entities["dish_names"]]
            
        # Ensure other required fields have default values
        for field in ["restaurant_name", "utilities", "styles",
                      "ward_name", "district_name", "city_name"]:
            if field not in entities:
                entities[field] = ""
                
        if "index_name" not in entities or not entities["index_name"]:
            entities["index_name"] = ELASTICSEARCH_INDEX
                
        # Get common filters
        filter_query = self.create_common_filters(entities=entities)

        dish_queries = self.create_dish_query(dish_names=entities["dish_names"])

        # Construct the main query
        query = {
            "bool": {
                "must": [*filter_query["bool"]["must"]],
                "filter": [*filter_query["bool"]["filter"]],
                "should": [
                    *filter_query["bool"].get("should", []),
                    *dish_queries,
                ],
                "must_not": [*filter_query["bool"].get("must_not", [])],
                "boost": 1,
            },
        }

        result = {
            "index": entities["index_name"],
            "query": query,
            "size": top_k,
            "_source": True,  # Using _source instead of source which is more standard
        }

        return result

    def create_common_filters(
        self, entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create optimized common filter conditions used in both regular and semantic queries

        Args:
            entities (Dict[str, Any]): Entities from user's message

        Returns:
            Dict[str, Any]: Filter query configuration
        """
        filter_conditions = []
        must_conditions = []
        must_not_conditions = []
        should_conditions = []

        fields_with_accent = [
            "without_accent_normalized_analyzer",
            "with_accent_normalized_analyzer",
        ]

        for entity in [
            "ward_name",
            "district_name",
            "city_name",
        ]:
            if entities.get(entity):
                must_conditions.append(
                    {
                        "multi_match": {
                            "query": entities[entity],
                            "fields": [
                                f"{entity}.{field}"
                                for field in fields_with_accent
                            ],
                            "type": "phrase_prefix",
                        }
                    }
                )

        # Restaurant name filter
        if entities.get("restaurant_name"):
            must_conditions.append(
                {
                    "match_phrase_prefix": {
                        "store_name": {
                            "query": entities["restaurant_name"],
                            "boost": 1,
                        },
                    }
                }
            )

        # Utilities and Styles filters - combine into single should clause
        utility_style_conditions = []

        if entities.get("utilities"):
            for utility in entities["utilities"]:
                utility_style_conditions.append(
                    {
                        "match": {
                            "utility": {
                                "query": utility,
                                "boost": 1,
                            }
                        }
                    }
                )

        if entities.get("styles"):
            for style in entities["styles"]:
                utility_style_conditions.append(
                    {
                        "match": {
                            "ambience": {
                                "query": style,
                                "boost": 1,
                            }
                        }
                    }
                )

        if utility_style_conditions:
            should_conditions.append(
                {
                    "bool": {
                        "should": utility_style_conditions,
                    }
                }
            )

        # Price filters
        if "avg_price" in entities:
            avg_price = entities["avg_price"]
            if avg_price:
                range_query = {"gte": avg_price * 0.8, "lte": avg_price * 1.2}
                filter_conditions.append({"range": {"avg_price": range_query}})

        # Combine all conditions
        return {
            "bool": {
                "filter": filter_conditions,
                "must": must_conditions,
                "should": should_conditions,
                "must_not": must_not_conditions,
            }
        }

    def create_dish_query(
        self,
        dish_names: List[str],
    ) -> List[Dict[str, Any]]:
        """Create query components for dish names

        Args:
            dish_names (List[str]): List of dish names to search for

        Returns:
            List[Dict[str, Any]]: List of query components for dish names
        """
        # Handle dish names
        dish_queries = []
        if dish_names:
            for dish_name in dish_names:
                if dish_name:  # Only add non-empty dish names
                    dish_queries.extend(
                        [
                            {
                                "match_phrase": {
                                    "store_name": {
                                        "query": dish_name,
                                        "boost": 2,
                                    }
                                }
                            },
                            {
                                "match_phrase": {
                                    "dish_name": {
                                        "query": dish_name,
                                        "boost": 1,
                                    }
                                }
                            },
                        ]
                    )
        return dish_queries

