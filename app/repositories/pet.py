"""Pet repository for database operations."""

from typing import Any

from sqlalchemy import or_, select

from app.models.pet import Pet
from app.repositories.base import BaseRepository
from app.schemas.pet import PetCreate, PetUpdate


class PetRepository(BaseRepository[Pet, PetCreate, PetUpdate]):
    """Repository for Pet CRUD operations."""

    @property
    def model(self) -> type[Pet]:
        """Return the Pet model class."""
        return Pet

    async def get_by_name(self, name: str) -> Pet | None:
        """Get a pet by name."""
        query = select(Pet).where(Pet.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_type(
        self, pet_type: str, *, skip: int = 0, limit: int = 100
    ) -> list[Pet]:
        """Get all pets of a specific type."""
        query = select(Pet).where(Pet.pet_type == pet_type).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def search(
        self, *, query_str: str, skip: int = 0, limit: int = 100
    ) -> list[Pet]:
        """Search pets by name or type."""
        search_pattern = f"%{query_str}%"
        query = (
            select(Pet)
            .where(
                or_(Pet.name.ilike(search_pattern), Pet.pet_type.ilike(search_pattern))
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_multi_with_filters(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        name: str | None = None,
        pet_type: str | None = None,
    ) -> list[Pet]:
        """Get multiple pets with optional filters."""
        query = select(Pet)

        if name:
            query = query.where(Pet.name.ilike(f"%{name}%"))

        if pet_type:
            query = query.where(Pet.pet_type == pet_type)

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_types(self) -> list[str]:
        """Get all unique pet types."""
        query = select(Pet.pet_type).distinct()
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def bulk_create(self, *, pets_in: list[PetCreate]) -> list[Pet]:
        """Create multiple pets at once."""
        db_pets = [Pet(**pet_in.model_dump()) for pet_in in pets_in]
        self.db.add_all(db_pets)
        await self.db.commit()

        # Refresh all objects to get their IDs
        for db_pet in db_pets:
            await self.db.refresh(db_pet)

        return db_pets

    async def update_by_name(
        self, *, name: str, pet_in: PetUpdate | dict[str, Any]
    ) -> Pet | None:
        """Update a pet by name."""
        pet = await self.get_by_name(name=name)
        if not pet:
            return None
        return await self.update(db_obj=pet, obj_in=pet_in)
