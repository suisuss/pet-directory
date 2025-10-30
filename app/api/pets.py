from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.pet import Pet
from app.schemas.pet import PetCreate, PetUpdate, PetResponse

router = APIRouter(prefix="/api/pets", tags=["pets"])


@router.post("/", response_model=PetResponse, status_code=201)
async def create_pet(
    pet: PetCreate,
    db: AsyncSession = Depends(get_db)
) -> Pet:
    """Create a new pet in the directory."""
    db_pet = Pet(**pet.model_dump())
    db.add(db_pet)
    await db.commit()
    await db.refresh(db_pet)
    return db_pet


@router.get("/", response_model=List[PetResponse])
async def list_pets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
) -> List[Pet]:
    """List all pets with optional pagination."""
    result = await db.execute(
        select(Pet)
        .offset(skip)
        .limit(limit)
        .order_by(Pet.created_at.desc())
    )
    pets = result.scalars().all()
    return pets


@router.get("/{pet_id}", response_model=PetResponse)
async def get_pet(
    pet_id: int,
    db: AsyncSession = Depends(get_db)
) -> Pet:
    """Get a specific pet by ID."""
    result = await db.execute(select(Pet).filter(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    return pet


@router.put("/{pet_id}", response_model=PetResponse)
async def update_pet(
    pet_id: int,
    pet_update: PetUpdate,
    db: AsyncSession = Depends(get_db)
) -> Pet:
    """Update a pet's information."""
    # First check if pet exists
    result = await db.execute(select(Pet).filter(Pet.id == pet_id))
    existing_pet = result.scalar_one_or_none()
    
    if not existing_pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    # Update only provided fields
    update_data = pet_update.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(Pet)
            .where(Pet.id == pet_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(existing_pet)
    
    return existing_pet


@router.delete("/{pet_id}", status_code=204)
async def delete_pet(
    pet_id: int,
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete a pet from the directory."""
    # Check if pet exists
    result = await db.execute(select(Pet).filter(Pet.id == pet_id))
    existing_pet = result.scalar_one_or_none()
    
    if not existing_pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    await db.execute(delete(Pet).where(Pet.id == pet_id))
    await db.commit()