import asyncio
from typing import Any, Dict, List, Optional, Tuple

from elastic import ElasticSearchClient
from query import QueryCreator


class Searcher:
    """Service handling different types of restaurant searches and retrievals."""

    def __init__(
        self,
        elastic_search_client: ElasticSearchClient,
        query_creator: QueryCreator,
    ) -> None:
        """Initialize search service with required dependencies.

        Args:
            elastic_search_client: Client for Elasticsearch operations
            query_creator: Service to create search queries
        """
        self.elastic_search_client = elastic_search_client
        self.query_creator = query_creator

    async def search(
        self,
        entities: Dict[str, Any],
        top_k: int = 5,
    ) -> List[dict]:
        """Retrieve documents using keyword-based (lexical) search.

        Args:
            entities: Search parameters including keywords
            top_k: Number of results to return

        Returns:
            List of matched documents
        """
        query = self.query_creator.create_query(
            entities=entities, top_k=top_k
        )
        search_result = await self.elastic_search_client.search(
            query=query
        )
        output = []
        for item in search_result:
            if "_source" in item:
                source = item["_source"]
                source["score"] = item["_score"]
                output.append(source)
        return output


async def create_searcher():
    es_client = await ElasticSearchClient.create()
    return Searcher(
        elastic_search_client=es_client,
        query_creator=QueryCreator(),
    )
