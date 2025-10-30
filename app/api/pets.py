"""Pet API endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.pet import Pet
from app.schemas.pet import PetCreate, PetResponse, PetUpdate

router: APIRouter = APIRouter(
    prefix="/api/pets",
    tags=["pets"],
    responses={
        404: {"description": "Pet not found"},
        400: {"description": "Invalid request"},
    },
)

# Type alias for dependency injection
DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/",
    response_model=PetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new pet",
    response_description="The created pet",
)
async def create_pet(
    pet: PetCreate,
    db: DbSession,
) -> Pet:
    """
    Create a new pet in the directory.

    Args:
        pet: Pet data for creation
        db: Database session

    Returns:
        Created pet with generated ID and timestamp

    Raises:
        HTTPException: If there's an error creating the pet
    """
    try:
        db_pet: Pet = Pet(**pet.model_dump())
        db.add(db_pet)
        await db.commit()
        await db.refresh(db_pet)
        return db_pet
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create pet due to data integrity error",
        ) from e
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        ) from e


@router.get(
    "/",
    response_model=list[PetResponse],
    summary="List all pets",
    response_description="List of pets",
)
async def list_pets(
    db: DbSession,
    skip: Annotated[int, Query(ge=0, description="Number of pets to skip")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=1000, description="Maximum number of pets to return")
    ] = 100,
    pet_type: Annotated[str | None, Query(description="Filter by pet type")] = None,
) -> list[Pet]:
    """
    List all pets with optional pagination and filtering.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        pet_type: Optional filter by pet type
        db: Database session

    Returns:
        List of pets matching the criteria
    """
    try:
        query = select(Pet)

        if pet_type:
            query = query.filter(Pet.pet_type == pet_type.lower())

        query = query.offset(skip).limit(limit).order_by(Pet.created_at.desc())

        result = await db.execute(query)
        pets: list[Pet] = list(result.scalars().all())
        return pets
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        ) from e


@router.get(
    "/{pet_id}",
    response_model=PetResponse,
    summary="Get a specific pet",
    response_description="The requested pet",
)
async def get_pet(
    pet_id: Annotated[int, Path(ge=1, description="The ID of the pet to retrieve")],
    db: DbSession,
) -> Pet:
    """
    Get a specific pet by ID.

    Args:
        pet_id: ID of the pet to retrieve
        db: Database session

    Returns:
        Pet with the specified ID

    Raises:
        HTTPException: If pet is not found
    """
    result = await db.execute(select(Pet).filter(Pet.id == pet_id))
    pet: Pet | None = result.scalar_one_or_none()

    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pet with ID {pet_id} not found",
        )

    return pet


@router.put(
    "/{pet_id}",
    response_model=PetResponse,
    summary="Update a pet",
    response_description="The updated pet",
)
async def update_pet(
    pet_id: Annotated[int, Path(ge=1, description="The ID of the pet to update")],
    pet_update: PetUpdate,
    db: DbSession,
) -> Pet:
    """
    Update a pet's information.

    Args:
        pet_id: ID of the pet to update
        pet_update: Fields to update
        db: Database session

    Returns:
        Updated pet

    Raises:
        HTTPException: If pet is not found or update fails
    """
    # First check if pet exists
    result = await db.execute(select(Pet).filter(Pet.id == pet_id))
    existing_pet: Pet | None = result.scalar_one_or_none()

    if not existing_pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pet with ID {pet_id} not found",
        )

    # Update only provided fields
    update_data: dict[str, Any] = pet_update.model_dump(exclude_unset=True)

    if update_data:
        try:
            await db.execute(update(Pet).where(Pet.id == pet_id).values(**update_data))
            await db.commit()
            await db.refresh(existing_pet)
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update pet due to data integrity error",
            ) from e
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            ) from e

    return existing_pet


@router.delete(
    "/{pet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a pet",
    response_description="Pet deleted successfully",
)
async def delete_pet(
    pet_id: Annotated[int, Path(ge=1, description="The ID of the pet to delete")],
    db: DbSession,
) -> None:
    """
    Delete a pet from the directory.

    Args:
        pet_id: ID of the pet to delete
        db: Database session

    Raises:
        HTTPException: If pet is not found or deletion fails
    """
    # Check if pet exists
    result = await db.execute(select(Pet).filter(Pet.id == pet_id))
    existing_pet: Pet | None = result.scalar_one_or_none()

    if not existing_pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pet with ID {pet_id} not found",
        )

    try:
        await db.execute(delete(Pet).where(Pet.id == pet_id))
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete pet",
        ) from e


@router.get(
    "/stats/summary",
    response_model=dict[str, Any],
    summary="Get pet statistics",
    response_description="Summary statistics about pets",
)
async def get_pet_stats(db: DbSession) -> dict[str, Any]:
    """
    Get summary statistics about pets in the directory.

    Args:
        db: Database session

    Returns:
        Dictionary with pet statistics
    """
    try:
        # Get total count
        total_result = await db.execute(select(func.count(Pet.id)))
        total_count: int = total_result.scalar() or 0

        # Get counts by type
        type_counts_result = await db.execute(
            select(Pet.pet_type, func.count(Pet.id))
            .group_by(Pet.pet_type)
            .order_by(Pet.pet_type)
        )
        type_rows = type_counts_result.all()
        type_counts: dict[str, int] = {str(row[0]): int(row[1]) for row in type_rows}

        return {
            "total_pets": total_count,
            "pets_by_type": type_counts,
        }
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics",
        ) from e
