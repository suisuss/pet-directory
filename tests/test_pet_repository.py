"""Tests for PetRepository and BaseRepository functionality."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pet import Pet
from app.repositories.pet import PetRepository
from app.schemas.pet import PetCreate, PetUpdate


@pytest.fixture
def pet_repo(test_db: AsyncSession) -> PetRepository:
    """Create a PetRepository instance with test database."""
    return PetRepository(db=test_db)


class TestBaseRepositoryMethods:
    """Test inherited BaseRepository methods."""

    async def test_create(self, pet_repo: PetRepository) -> None:
        """Test creating a new pet."""
        pet_in = PetCreate(name="Buddy", pet_type="dog")
        pet = await pet_repo.create(obj_in=pet_in)

        assert pet.id is not None
        assert pet.name == "Buddy"
        assert pet.pet_type == "dog"
        assert pet.created_at is not None

    async def test_get_existing_pet(self, pet_repo: PetRepository) -> None:
        """Test getting an existing pet by ID."""
        # Create a pet first
        pet_in = PetCreate(name="Whiskers", pet_type="cat")
        created_pet = await pet_repo.create(obj_in=pet_in)

        # Get the pet
        retrieved_pet = await pet_repo.get(id=created_pet.id)

        assert retrieved_pet is not None
        assert retrieved_pet.id == created_pet.id
        assert retrieved_pet.name == "Whiskers"
        assert retrieved_pet.pet_type == "cat"

    async def test_get_nonexistent_pet(self, pet_repo: PetRepository) -> None:
        """Test getting a nonexistent pet returns None."""
        pet = await pet_repo.get(id=999)
        assert pet is None

    async def test_get_multi_no_filters(self, pet_repo: PetRepository) -> None:
        """Test getting multiple pets without filters."""
        # Create multiple pets
        pets_data = [
            PetCreate(name="Buddy", pet_type="dog"),
            PetCreate(name="Whiskers", pet_type="cat"),
            PetCreate(name="Tweety", pet_type="bird"),
        ]
        for pet_in in pets_data:
            await pet_repo.create(obj_in=pet_in)

        # Get all pets
        pets = await pet_repo.get_multi()

        assert len(pets) == 3
        assert {pet.name for pet in pets} == {"Buddy", "Whiskers", "Tweety"}

    async def test_get_multi_with_pagination(self, pet_repo: PetRepository) -> None:
        """Test getting multiple pets with pagination."""
        # Create multiple pets
        for i in range(5):
            pet_in = PetCreate(name=f"Pet{i}", pet_type="dog")
            await pet_repo.create(obj_in=pet_in)

        # Get pets with pagination
        pets_page1 = await pet_repo.get_multi(skip=0, limit=2)
        pets_page2 = await pet_repo.get_multi(skip=2, limit=2)

        assert len(pets_page1) == 2
        assert len(pets_page2) == 2
        assert pets_page1[0].name != pets_page2[0].name

    async def test_get_multi_with_filters(self, pet_repo: PetRepository) -> None:
        """Test getting multiple pets with filters."""
        # Create pets with different types
        await pet_repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Max", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Whiskers", pet_type="cat"))

        # Filter by pet_type
        dogs = await pet_repo.get_multi(pet_type="dog")

        assert len(dogs) == 2
        assert all(pet.pet_type == "dog" for pet in dogs)

    async def test_update_pet(self, pet_repo: PetRepository) -> None:
        """Test updating a pet."""
        # Create a pet
        pet_in = PetCreate(name="Buddy", pet_type="dog")
        pet = await pet_repo.create(obj_in=pet_in)

        # Update the pet
        update_data = PetUpdate(name="Buddy Jr.")
        updated_pet = await pet_repo.update(db_obj=pet, obj_in=update_data)

        assert updated_pet.id == pet.id
        assert updated_pet.name == "Buddy Jr."
        assert updated_pet.pet_type == "dog"  # Unchanged

    async def test_update_pet_with_dict(self, pet_repo: PetRepository) -> None:
        """Test updating a pet with dictionary."""
        # Create a pet
        pet_in = PetCreate(name="Luna", pet_type="cat")
        pet = await pet_repo.create(obj_in=pet_in)

        # Update with dict
        update_data = {"pet_type": "kitten"}
        updated_pet = await pet_repo.update(db_obj=pet, obj_in=update_data)

        assert updated_pet.id == pet.id
        assert updated_pet.name == "Luna"  # Unchanged
        assert updated_pet.pet_type == "kitten"

    async def test_delete_existing_pet(self, pet_repo: PetRepository) -> None:
        """Test deleting an existing pet."""
        # Create a pet
        pet_in = PetCreate(name="Temporary", pet_type="dog")
        pet = await pet_repo.create(obj_in=pet_in)

        # Delete the pet
        deleted_pet = await pet_repo.delete(id=pet.id)

        assert deleted_pet is not None
        assert deleted_pet.id == pet.id

        # Verify it's gone
        retrieved_pet = await pet_repo.get(id=pet.id)
        assert retrieved_pet is None

    async def test_delete_nonexistent_pet(self, pet_repo: PetRepository) -> None:
        """Test deleting a nonexistent pet returns None."""
        deleted_pet = await pet_repo.delete(id=999)
        assert deleted_pet is None

    async def test_count_no_filters(self, pet_repo: PetRepository) -> None:
        """Test counting all pets."""
        # Create multiple pets
        for i in range(5):
            await pet_repo.create(obj_in=PetCreate(name=f"Pet{i}", pet_type="dog"))

        count = await pet_repo.count()
        assert count == 5

    async def test_count_with_filters(self, pet_repo: PetRepository) -> None:
        """Test counting pets with filters."""
        # Create pets with different types
        await pet_repo.create(obj_in=PetCreate(name="Dog1", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Dog2", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Cat1", pet_type="cat"))

        count = await pet_repo.count(pet_type="dog")
        assert count == 2

    async def test_count_empty_database(self, pet_repo: PetRepository) -> None:
        """Test counting pets in empty database."""
        count = await pet_repo.count()
        assert count == 0

    async def test_exists_true(self, pet_repo: PetRepository) -> None:
        """Test exists returns True for existing pet."""
        pet_in = PetCreate(name="Buddy", pet_type="dog")
        pet = await pet_repo.create(obj_in=pet_in)

        exists = await pet_repo.exists(id=pet.id)
        assert exists is True

    async def test_exists_false(self, pet_repo: PetRepository) -> None:
        """Test exists returns False for nonexistent pet."""
        exists = await pet_repo.exists(id=999)
        assert exists is False


class TestPetRepositorySpecificMethods:
    """Test PetRepository-specific methods."""

    async def test_get_by_name_existing(self, pet_repo: PetRepository) -> None:
        """Test getting a pet by name when it exists."""
        await pet_repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))

        pet = await pet_repo.get_by_name(name="Buddy")

        assert pet is not None
        assert pet.name == "Buddy"
        assert pet.pet_type == "dog"

    async def test_get_by_name_nonexistent(self, pet_repo: PetRepository) -> None:
        """Test getting a pet by name when it doesn't exist."""
        pet = await pet_repo.get_by_name(name="Nonexistent")
        assert pet is None

    async def test_get_by_name_case_sensitive(self, pet_repo: PetRepository) -> None:
        """Test that get_by_name is case-sensitive."""
        await pet_repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))

        pet = await pet_repo.get_by_name(name="buddy")
        assert pet is None

    async def test_get_by_type(self, pet_repo: PetRepository) -> None:
        """Test getting all pets of a specific type."""
        # Create pets with different types
        await pet_repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Max", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Whiskers", pet_type="cat"))

        dogs = await pet_repo.get_by_type(pet_type="dog")

        assert len(dogs) == 2
        assert all(pet.pet_type == "dog" for pet in dogs)
        assert {pet.name for pet in dogs} == {"Buddy", "Max"}

    async def test_get_by_type_with_pagination(self, pet_repo: PetRepository) -> None:
        """Test getting pets by type with pagination."""
        # Create multiple dogs
        for i in range(5):
            await pet_repo.create(obj_in=PetCreate(name=f"Dog{i}", pet_type="dog"))

        dogs = await pet_repo.get_by_type(pet_type="dog", skip=1, limit=2)

        assert len(dogs) == 2

    async def test_get_by_type_empty(self, pet_repo: PetRepository) -> None:
        """Test getting pets by type when none exist."""
        pets = await pet_repo.get_by_type(pet_type="dragon")
        assert len(pets) == 0

    async def test_search_by_name(self, pet_repo: PetRepository) -> None:
        """Test searching pets by name."""
        await pet_repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Whiskers", pet_type="cat"))

        results = await pet_repo.search(query_str="Bud")

        assert len(results) == 1
        assert results[0].name == "Buddy"

    async def test_search_by_type(self, pet_repo: PetRepository) -> None:
        """Test searching pets by type."""
        await pet_repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Max", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Whiskers", pet_type="cat"))

        results = await pet_repo.search(query_str="dog")

        assert len(results) == 2
        assert all(pet.pet_type == "dog" for pet in results)

    async def test_search_case_insensitive(self, pet_repo: PetRepository) -> None:
        """Test that search is case-insensitive."""
        await pet_repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))

        results_upper = await pet_repo.search(query_str="BUDDY")
        results_lower = await pet_repo.search(query_str="buddy")

        assert len(results_upper) == 1
        assert len(results_lower) == 1
        assert results_upper[0].name == results_lower[0].name

    async def test_search_partial_match(self, pet_repo: PetRepository) -> None:
        """Test searching with partial string match."""
        await pet_repo.create(obj_in=PetCreate(name="Whiskers", pet_type="cat"))
        await pet_repo.create(obj_in=PetCreate(name="WhiskeyJack", pet_type="bird"))

        results = await pet_repo.search(query_str="whisk")

        assert len(results) == 2
        assert {pet.name for pet in results} == {"Whiskers", "WhiskeyJack"}

    async def test_search_with_pagination(self, pet_repo: PetRepository) -> None:
        """Test search with pagination."""
        for i in range(5):
            await pet_repo.create(obj_in=PetCreate(name=f"Dog{i}", pet_type="dog"))

        results = await pet_repo.search(query_str="dog", skip=1, limit=2)

        assert len(results) == 2

    async def test_search_no_results(self, pet_repo: PetRepository) -> None:
        """Test searching when no results match."""
        await pet_repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))

        results = await pet_repo.search(query_str="elephant")

        assert len(results) == 0

    async def test_get_multi_with_filters_name_only(
        self, pet_repo: PetRepository
    ) -> None:
        """Test get_multi_with_filters with name filter only."""
        await pet_repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Buddy Jr", pet_type="cat"))
        await pet_repo.create(obj_in=PetCreate(name="Max", pet_type="dog"))

        results = await pet_repo.get_multi_with_filters(name="Buddy")

        assert len(results) == 2
        assert all("Buddy" in pet.name for pet in results)

    async def test_get_multi_with_filters_type_only(
        self, pet_repo: PetRepository
    ) -> None:
        """Test get_multi_with_filters with pet_type filter only."""
        await pet_repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Max", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Whiskers", pet_type="cat"))

        results = await pet_repo.get_multi_with_filters(pet_type="dog")

        assert len(results) == 2
        assert all(pet.pet_type == "dog" for pet in results)

    async def test_get_multi_with_filters_both(self, pet_repo: PetRepository) -> None:
        """Test get_multi_with_filters with both filters."""
        await pet_repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Buddy Jr", pet_type="cat"))
        await pet_repo.create(obj_in=PetCreate(name="Max", pet_type="dog"))

        results = await pet_repo.get_multi_with_filters(name="Buddy", pet_type="dog")

        assert len(results) == 1
        assert results[0].name == "Buddy"
        assert results[0].pet_type == "dog"

    async def test_get_multi_with_filters_pagination(
        self, pet_repo: PetRepository
    ) -> None:
        """Test get_multi_with_filters with pagination."""
        for i in range(5):
            await pet_repo.create(obj_in=PetCreate(name=f"Dog{i}", pet_type="dog"))

        results = await pet_repo.get_multi_with_filters(pet_type="dog", skip=1, limit=2)

        assert len(results) == 2

    async def test_get_multi_with_filters_no_filters(
        self, pet_repo: PetRepository
    ) -> None:
        """Test get_multi_with_filters without any filters."""
        await pet_repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Whiskers", pet_type="cat"))

        results = await pet_repo.get_multi_with_filters()

        assert len(results) == 2

    async def test_get_types(self, pet_repo: PetRepository) -> None:
        """Test getting all unique pet types."""
        await pet_repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Max", pet_type="dog"))
        await pet_repo.create(obj_in=PetCreate(name="Whiskers", pet_type="cat"))
        await pet_repo.create(obj_in=PetCreate(name="Tweety", pet_type="bird"))

        types = await pet_repo.get_types()

        assert len(types) == 3
        assert set(types) == {"dog", "cat", "bird"}

    async def test_get_types_empty(self, pet_repo: PetRepository) -> None:
        """Test getting types from empty database."""
        types = await pet_repo.get_types()
        assert len(types) == 0

    async def test_bulk_create(self, pet_repo: PetRepository) -> None:
        """Test creating multiple pets at once."""
        pets_in = [
            PetCreate(name="Buddy", pet_type="dog"),
            PetCreate(name="Whiskers", pet_type="cat"),
            PetCreate(name="Tweety", pet_type="bird"),
        ]

        created_pets = await pet_repo.bulk_create(pets_in=pets_in)

        assert len(created_pets) == 3
        assert all(pet.id is not None for pet in created_pets)
        assert {pet.name for pet in created_pets} == {"Buddy", "Whiskers", "Tweety"}

    async def test_bulk_create_empty_list(self, pet_repo: PetRepository) -> None:
        """Test bulk_create with empty list."""
        created_pets = await pet_repo.bulk_create(pets_in=[])
        assert len(created_pets) == 0

    async def test_update_by_name_existing(self, pet_repo: PetRepository) -> None:
        """Test updating a pet by name when it exists."""
        await pet_repo.create(obj_in=PetCreate(name="Buddy", pet_type="dog"))

        updated_pet = await pet_repo.update_by_name(
            name="Buddy", pet_in=PetUpdate(pet_type="puppy")
        )

        assert updated_pet is not None
        assert updated_pet.name == "Buddy"
        assert updated_pet.pet_type == "puppy"

    async def test_update_by_name_nonexistent(self, pet_repo: PetRepository) -> None:
        """Test updating a pet by name when it doesn't exist."""
        updated_pet = await pet_repo.update_by_name(
            name="Nonexistent", pet_in=PetUpdate(pet_type="dog")
        )

        assert updated_pet is None

    async def test_update_by_name_with_dict(self, pet_repo: PetRepository) -> None:
        """Test updating a pet by name with dictionary."""
        await pet_repo.create(obj_in=PetCreate(name="Luna", pet_type="cat"))

        updated_pet = await pet_repo.update_by_name(
            name="Luna", pet_in={"name": "Luna Belle"}
        )

        assert updated_pet is not None
        assert updated_pet.name == "Luna Belle"
        assert updated_pet.pet_type == "cat"
