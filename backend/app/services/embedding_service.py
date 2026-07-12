"""Embedding Service - semantic search for documents and summaries."""
import logging
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Record, VectorParams, Distance, Filter, FieldCondition, MatchValue

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for semantic search using embeddings."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        api_key: Optional[str] = None
    ):
        """
        Initialize Qdrant client.
        
        Args:
            host: Qdrant host
            port: Qdrant port
            api_key: API key (optional)
        """
        self.host = host
        self.port = port
        self.api_key = api_key
        
        # Build URL
        if api_key:
            url = f"http://{host}:{port}"
        else:
            url = f"http://{host}:{port}"
        
        self.client = QdrantClient(url=url, api_key=api_key)
    
    async def initialize(self) -> None:
        """Initialize Qdrant collections."""
        # Create collections if they don't exist
        collections = ["manuals", "papers", "summaries"]
        
        for collection in collections:
            try:
                self.client.get_collection(collection)
            except Exception:
                # Collection doesn't exist, create it
                self.client.recreate_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI embedding dimension
                        distance=Distance.COSINE
                    )
                )
    
    async def search_similar(
        self,
        query: str,
        collection: str,
        top_k: int = 5,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Query text (will be embedded)
            collection: Collection to search
            top_k: Number of results
            filter_conditions: Filter criteria
            
        Returns:
            List of matching documents with scores
        """
        # In production, you would embed the query using OpenAI
        # For now, we'll use a placeholder approach
        
        try:
            # Try to get collection info first
            self.client.get_collection(collection)
            
            # Build filter if provided
            search_filter = None
            if filter_conditions:
                conditions = [
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                    for key, value in filter_conditions.items()
                ]
                search_filter = Filter(must=conditions)
            
            # Perform search (placeholder - would use actual embeddings)
            results = self.client.search(
                collection_name=collection,
                query_vector=[0.1] * 1536,  # Placeholder
                filter=search_filter,
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )
            
            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                for result in results
            ]
            
        except Exception as e:
            logger.warning(f"Search failed: {e}")
            return []
    
    async def search_manuals(
        self,
        query: str,
        crop: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search in DSSAT manuals.
        
        Args:
            query: Search query
            crop: Filter by crop (optional)
            top_k: Number of results
            
        Returns:
            Matching manual sections
        """
        filter_conditions = None
        if crop:
            filter_conditions = {"crop": crop}
        
        return await self.search_similar(
            query=query,
            collection="manuals",
            top_k=top_k,
            filter_conditions=filter_conditions
        )
    
    async def search_papers(
        self,
        query: str,
        year: Optional[int] = None,
        crop: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search research papers.
        
        Args:
            query: Search query
            year: Filter by year (optional)
            crop: Filter by crop (optional)
            top_k: Number of results
            
        Returns:
            Matching papers
        """
        filter_conditions = {}
        if year:
            filter_conditions["year"] = year
        if crop:
            filter_conditions["crop"] = crop
        
        return await self.search_similar(
            query=query,
            collection="papers",
            top_k=top_k,
            filter_conditions=filter_conditions
        )
    
    async def search_summaries(
        self,
        query: str,
        country: Optional[str] = None,
        state: Optional[str] = None,
        crop: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search simulation summaries.
        
        Args:
            query: Search query
            country: Filter by country (optional)
            state: Filter by state (optional)
            crop: Filter by crop (optional)
            top_k: Number of results
            
        Returns:
            Matching summaries
        """
        filter_conditions = {}
        if country:
            filter_conditions["country"] = country
        if state:
            filter_conditions["state"] = state
        if crop:
            filter_conditions["crop"] = crop
        
        return await self.search_similar(
            query=query,
            collection="summaries",
            top_k=top_k,
            filter_conditions=filter_conditions
        )
    
    async def add_document(
        self,
        collection: str,
        document_id: str,
        text: str,
        payload: Dict[str, Any]
    ) -> None:
        """
        Add a document to the collection.
        
        Args:
            collection: Collection name
            document_id: Document ID
            text: Text to embed
            payload: Metadata payload
        """
        # In production, you would embed the text using OpenAI
        # For now, we'll use a placeholder
        
        try:
            self.client.upsert(
                collection_name=collection,
                points=[
                    Record(
                        id=document_id,
                        vector=[0.1] * 1536,  # Placeholder
                        payload=payload
                    )
                ]
            )
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
    
    async def get_collection_info(self, collection: str) -> Dict[str, Any]:
        """
        Get collection information.
        
        Args:
            collection: Collection name
            
        Returns:
            Collection statistics
        """
        try:
            info = self.client.get_collection(collection)
            return {
                "name": collection,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            logger.warning(f"Collection not found: {e}")
            return {"name": collection, "error": str(e)}
