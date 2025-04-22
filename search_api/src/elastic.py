import logging
import os
import sys
from typing import Dict, Any, List, Optional
from elasticsearch import AsyncElasticsearch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
ELASTICSEARCH_INDEX = "chatbot"


class ElasticSearchClient:
    """Client for interacting with Elasticsearch."""

    def __init__(self, es_client: AsyncElasticsearch) -> None:
        """Initialize the client with an Elasticsearch instance.

        Args:
            es_client: An instance of AsyncElasticsearch.
        """
        self.es_client = es_client
        logger.info("ElasticSearchClient initialized")

    @classmethod
    async def create(cls, hosts: Optional[List[str]] = None) -> "ElasticSearchClient":
        """Factory method to create an ElasticSearchClient instance.

        Args:
            hosts: List of Elasticsearch hosts. Defaults to ELASTICSEARCH_URL.

        Returns:
            A new ElasticSearchClient instance.
        """
        if hosts is None:
            hosts = [ELASTICSEARCH_URL]
        
        logger.info(f"Creating ElasticSearchClient with hosts: {hosts}")
        
        # Configure client with explicit headers to avoid media type errors
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Create client with explicit headers and error retry options
        client = AsyncElasticsearch(
            hosts=hosts,
            headers=headers,
            retry_on_timeout=True,
            max_retries=3
        )
        
        return cls(client)

    async def search(
            self,
            query: Dict[str, Any],
            index: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Execute a search query against Elasticsearch.

        Args:
            query: The search query to execute.
            index: The index to search. Defaults to ELASTICSEARCH_INDEX.

        Returns:
            A list of search results.
        """
        if index is None:
            # Use the index from the query if available, otherwise use default
            index = query.get("index") if isinstance(query, dict) and "index" in query else ELASTICSEARCH_INDEX
            
            # Remove the index from the query if it's there
            if isinstance(query, dict) and "index" in query:
                query_body = {k: v for k, v in query.items() if k != "index"}
            else:
                query_body = query
        else:
            query_body = query

        logger.info(f"Executing search on index: {index}")
        logger.debug(f"Search query: {query_body}")
        
        try:
            response = await self.es_client.search(index=index, body=query_body)
            hits_count = len(response["hits"]["hits"])
            logger.info(f"Search returned {hits_count} results")
            return response["hits"]["hits"]
        except Exception as e:
            logger.error(f"Error searching Elasticsearch: {str(e)}", exc_info=True)
            raise Exception(f"Error searching Elasticsearch: {str(e)}")
            
    async def index_documents(
            self, 
            documents: List[Dict[str, Any]], 
            index: str = ELASTICSEARCH_INDEX,
            refresh: bool = True
    ) -> Dict[str, Any]:
        """Index multiple documents into Elasticsearch.
        
        Args:
            documents: List of documents to index
            index: The index to write to. Defaults to ELASTICSEARCH_INDEX.
            refresh: Whether to refresh the index after indexing. Defaults to True.
            
        Returns:
            Dictionary with indexing statistics
        """
        if not documents:
            logger.warning("No documents provided for indexing")
            return {"indexed": 0, "errors": 0, "error_details": []}

        # Check and create index with a more robust approach
        index_exists = await self.es_client.indices.exists(index=index)
        logger.info(f"Index '{index}' exists: {index_exists}")
            
        # Create index if it doesn't exist
        if not index_exists:
            logger.info(f"Creating index '{index}' with custom mapping")
            # Create index with mapping that supports accent-insensitive search
            mapping = {
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "with_accent_normalized_analyzer": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": ["lowercase"]
                            },
                            "without_accent_normalized_analyzer": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": ["lowercase", "asciifolding"]
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "store_name": {"type": "text"},
                        "dish_name": {"type": "text"},
                        "avg_price": {"type": "integer"},
                        "utility": {"type": "text"},
                        "ambience": {"type": "text"},
                        "ward_name": {
                            "type": "text",
                            "fields": {
                                "with_accent_normalized_analyzer": {"type": "text", "analyzer": "with_accent_normalized_analyzer"},
                                "without_accent_normalized_analyzer": {"type": "text", "analyzer": "without_accent_normalized_analyzer"}
                            }
                        },
                        "district_name": {
                            "type": "text", 
                            "fields": {
                                "with_accent_normalized_analyzer": {"type": "text", "analyzer": "with_accent_normalized_analyzer"},
                                "without_accent_normalized_analyzer": {"type": "text", "analyzer": "without_accent_normalized_analyzer"}
                            }
                        },
                        "city_name": {
                            "type": "text",
                            "fields": {
                                "with_accent_normalized_analyzer": {"type": "text", "analyzer": "with_accent_normalized_analyzer"},
                                "without_accent_normalized_analyzer": {"type": "text", "analyzer": "without_accent_normalized_analyzer"}
                            }
                        }
                    }
                }
            }
            await self.es_client.indices.create(index=index, body=mapping)
            
        # Prepare bulk operation
        operations = []
        for doc in documents:
            operations.append({"index": {"_index": index}})
            operations.append(doc)
            
        try:
            logger.info(f"Executing bulk indexing operation with {len(operations)//2} documents")
            response = await self.es_client.bulk(body=operations, refresh=refresh)
            
            # Log at debug level due to potential size
            logger.info(f"Bulk indexing response: {response}")
            
            success_count = len([item for item in response["items"] if "error" not in item["index"]])
            errors = [item["index"]["error"] for item in response["items"] if "error" in item["index"]]
            
            if errors:
                logger.warning(f"Indexing completed with {len(errors)} errors")
                logger.info(f"Error details: {errors}")
            else:
                logger.info(f"Successfully indexed {success_count} documents")
            
            return {
                "indexed": success_count,
                "errors": len(errors),
                "error_details": errors
            }
        except Exception as e:
            logger.error(f"Error indexing documents: {str(e)}", exc_info=True)
            raise Exception(f"Error indexing documents: {str(e)}")

    async def close(self) -> None:
        """Close the Elasticsearch client connection."""
        logger.info("Closing Elasticsearch client connection")
        await self.es_client.close()
