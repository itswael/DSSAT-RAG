"""Base repository class."""
from typing import Any, Generic, TypeVar, Type, Optional, List, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import text

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository class with common CRUD operations."""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db

    async def get(self, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        return await self.db.get(self.model, id)

    async def get_by_field(
        self,
        field: str,
        value: Any,
        first: bool = True,
    ) -> Union[Optional[ModelType], List[ModelType]]:
        """
        Get records by field value.

        Args:
            field: Field name
            value: Field value
            first: Return only first record

        Returns:
            Single record or list of records
        """
        stmt = select(self.model).where(text(f"{field} = :value")).params(value=value)

        if first:
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        desc: bool = False,
    ) -> List[ModelType]:
        """
        Get all records with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field name to order by
            desc: Order descending

        Returns:
            List of records
        """
        stmt = select(self.model).offset(skip).limit(limit)

        if order_by:
            if desc:
                stmt = stmt.order_by(text(f"{order_by} DESC"))
            else:
                stmt = stmt.order_by(text(order_by))

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, obj: ModelType) -> ModelType:
        """
        Create a new record.

        Args:
            obj: SQLAlchemy model instance

        Returns:
            Created record
        """
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def create_bulk(self, objs: List[ModelType]) -> List[ModelType]:
        """
        Create multiple records.

        Args:
            objs: List of SQLAlchemy model instances

        Returns:
            List of created records
        """
        self.db.add_all(objs)
        await self.db.commit()
        for obj in objs:
            await self.db.refresh(obj)
        return objs

    async def update(
        self,
        db_obj: ModelType,
        update_data: dict[str, Any],
    ) -> ModelType:
        """
        Update a record.

        Args:
            db_obj: Existing database record
            update_data: Dictionary of fields to update

        Returns:
            Updated record
        """
        for field, value in update_data.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, obj: ModelType) -> None:
        """
        Delete a record.

        Args:
            obj: Record to delete
        """
        await self.db.delete(obj)
        await self.db.commit()

    async def delete_by_id(self, id: Any) -> bool:
        """
        Delete a record by ID.

        Args:
            id: Record ID

        Returns:
            True if deleted, False if not found
        """
        obj = await self.get(id)
        if obj:
            await self.delete(obj)
            return True
        return False
