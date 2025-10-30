"""Pet API endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.dependencies import get_pet_repository
from app.models.pet import Pet
from app.repositories.pet import PetRepository
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
RepoDep = Annotated[PetRepository, Depends(get_pet_repository)]


@router.post(
    "/",
    response_model=PetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new pet",
    response_description="The created pet",
)
async def create_pet(
    pet: PetCreate,
    repo: RepoDep,
) -> Pet:
    """
    Create a new pet in the directory.

    Args:
        pet: Pet data for creation
        repo: Pet repository

    Returns:
        Created pet with generated ID and timestamp

    Raises:
        HTTPException: If there's an error creating the pet
    """
    try:
        return await repo.create(obj_in=pet)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create pet due to data integrity error",
        ) from e
    except SQLAlchemyError as e:
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
    repo: RepoDep,
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
        repo: Pet repository

    Returns:
        List of pets matching the criteria
    """
    try:
        if pet_type:
            return await repo.get_by_type(
                pet_type=pet_type.lower(), skip=skip, limit=limit
            )
        return await repo.get_multi(skip=skip, limit=limit)
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
    repo: RepoDep,
) -> Pet:
    """
    Get a specific pet by ID.

    Args:
        pet_id: ID of the pet to retrieve
        repo: Pet repository

    Returns:
        Pet with the specified ID

    Raises:
        HTTPException: If pet is not found
    """
    pet = await repo.get(id=pet_id)
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
    repo: RepoDep,
) -> Pet:
    """
    Update a pet's information.

    Args:
        pet_id: ID of the pet to update
        pet_update: Fields to update
        repo: Pet repository

    Returns:
        Updated pet

    Raises:
        HTTPException: If pet is not found or update fails
    """
    # First check if pet exists
    existing_pet = await repo.get(id=pet_id)
    if not existing_pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pet with ID {pet_id} not found",
        )

    try:
        return await repo.update(db_obj=existing_pet, obj_in=pet_update)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update pet due to data integrity error",
        ) from e
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        ) from e


@router.delete(
    "/{pet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a pet",
    response_description="Pet deleted successfully",
)
async def delete_pet(
    pet_id: Annotated[int, Path(ge=1, description="The ID of the pet to delete")],
    repo: RepoDep,
) -> None:
    """
    Delete a pet from the directory.

    Args:
        pet_id: ID of the pet to delete
        repo: Pet repository

    Raises:
        HTTPException: If pet is not found or deletion fails
    """
    try:
        deleted_pet = await repo.delete(id=pet_id)
        if not deleted_pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pet with ID {pet_id} not found",
            )
    except SQLAlchemyError as e:
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
async def get_pet_stats(repo: RepoDep) -> dict[str, Any]:
    """
    Get summary statistics about pets in the directory.

    Args:
        repo: Pet repository

    Returns:
        Dictionary with pet statistics
    """
    try:
        # Get total count
        total_count = await repo.count()

        # Get all unique pet types
        pet_types = await repo.get_types()

        # Get counts by type
        type_counts: dict[str, int] = {}
        for pet_type in pet_types:
            count = await repo.count(pet_type=pet_type)
            type_counts[pet_type] = count

        return {
            "total_pets": total_count,
            "pets_by_type": type_counts,
        }
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics",
        ) from e
