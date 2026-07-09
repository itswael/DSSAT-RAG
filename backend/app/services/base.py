"""Base service class."""
from typing import Generic, TypeVar, List, Optional

from app.repositories.base import BaseRepository

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service class with common operations."""

    def __init__(self, repository: BaseRepository[ModelType]):
        """
        Initialize service.

        Args:
            repository: Repository instance
        """
        self.repository = repository

    async def get(self, id: int) -> Optional[ModelType]:
        """Get a single record by ID."""
        return await self.repository.get(id)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """
        Get all records with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of records
        """
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.

        Args:
            obj_in: Input schema for creation

        Returns:
            Created record
        """
        # Map schema to model (implementation in subclass)
        raise NotImplementedError

    async def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ) -> ModelType:
        """
        Update a record.

        Args:
            db_obj: Existing database record
            obj_in: Input schema with updates

        Returns:
            Updated record
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        return await self.repository.update(db_obj, update_data)

    async def delete(self, id: int) -> bool:
        """
        Delete a record by ID.

        Args:
            id: Record ID

        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete_by_id(id)
