"""Dependency injection for repositories."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.pet import PetRepository


async def get_pet_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PetRepository:
    """Get Pet repository instance."""
    return PetRepository(db)
