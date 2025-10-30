"""Base repository with common CRUD operations."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Abstract base repository with common CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.db = db

    @property
    @abstractmethod
    def model(self) -> type[ModelType]:
        """Return the SQLAlchemy model class."""
        pass

    async def get(self, id: int) -> ModelType | None:  # noqa: A002
        """Get a single record by ID."""
        query = select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100, **filters: Any
    ) -> list[ModelType]:
        """Get multiple records with pagination and filters."""
        query = select(self.model)

        # Apply filters
        for field, value in filters.items():
            if value is not None and hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self, *, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """Update an existing record."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, *, id: int) -> ModelType | None:  # noqa: A002
        """Delete a record by ID."""
        db_obj = await self.get(id=id)
        if db_obj:
            await self.db.delete(db_obj)
            await self.db.commit()
        return db_obj

    async def count(self, **filters: Any) -> int:
        """Count records with optional filters."""
        query = select(func.count()).select_from(self.model)

        # Apply filters
        for field, value in filters.items():
            if value is not None and hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def exists(self, id: int) -> bool:  # noqa: A002
        """Check if a record exists by ID."""
        query = select(func.count()).select_from(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        result = await self.db.execute(query)
        count = result.scalar() or 0
        return count > 0
