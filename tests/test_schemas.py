"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.pet import PetCreate, PetUpdate, PetResponse


class TestPetCreate:
    """Tests for PetCreate schema."""

    def test_valid_pet_create(self) -> None:
        """Test creating a valid PetCreate instance."""
        pet = PetCreate(name="Buddy", pet_type="dog")
        assert pet.name == "Buddy"
        assert pet.pet_type == "dog"

    def test_pet_type_lowercase_conversion(self) -> None:
        """Test that pet_type is converted to lowercase."""
        pet = PetCreate(name="Buddy", pet_type="DOG")
        assert pet.pet_type == "dog"

        pet = PetCreate(name="Whiskers", pet_type="CaT")
        assert pet.pet_type == "cat"

    def test_name_whitespace_stripping(self) -> None:
        """Test that name whitespace is stripped."""
        pet = PetCreate(name="  Buddy  ", pet_type="dog")
        assert pet.name == "Buddy"

    def test_empty_name_validation(self) -> None:
        """Test that empty names are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PetCreate(name="", pet_type="dog")
        # Pydantic returns "string should have at least 1 character" for empty strings
        assert "at least 1 character" in str(exc_info.value).lower()

        with pytest.raises(ValidationError) as exc_info:
            PetCreate(name="   ", pet_type="dog")
        # Whitespace gets stripped, resulting in the same error
        assert (
            "at least 1 character" in str(exc_info.value).lower()
            or "whitespace" in str(exc_info.value).lower()
        )

    def test_empty_pet_type_validation(self) -> None:
        """Test that empty pet types are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PetCreate(name="Buddy", pet_type="")
        # Pydantic returns "string should have at least 1 character" for empty strings
        assert "at least 1 character" in str(exc_info.value).lower()

    def test_missing_fields(self) -> None:
        """Test that missing required fields cause validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            PetCreate(name="Buddy")  # type: ignore
        assert "pet_type" in str(exc_info.value).lower()

        with pytest.raises(ValidationError) as exc_info:
            PetCreate(pet_type="dog")  # type: ignore
        assert "name" in str(exc_info.value).lower()

    def test_max_length_validation(self) -> None:
        """Test maximum length validation."""
        # Name max length is 100
        long_name = "a" * 101
        with pytest.raises(ValidationError) as exc_info:
            PetCreate(name=long_name, pet_type="dog")
        assert "100" in str(exc_info.value)

        # Pet type max length is 50
        long_type = "a" * 51
        with pytest.raises(ValidationError) as exc_info:
            PetCreate(name="Buddy", pet_type=long_type)
        assert "50" in str(exc_info.value)


class TestPetUpdate:
    """Tests for PetUpdate schema."""

    def test_valid_pet_update(self) -> None:
        """Test creating a valid PetUpdate instance."""
        pet = PetUpdate(name="Buddy", pet_type="dog")
        assert pet.name == "Buddy"
        assert pet.pet_type == "dog"

    def test_optional_fields(self) -> None:
        """Test that all fields are optional."""
        pet = PetUpdate()
        assert pet.name is None
        assert pet.pet_type is None

        pet = PetUpdate(name="Buddy")
        assert pet.name == "Buddy"
        assert pet.pet_type is None

        pet = PetUpdate(pet_type="cat")
        assert pet.name is None
        assert pet.pet_type == "cat"

    def test_pet_type_lowercase_conversion(self) -> None:
        """Test that pet_type is converted to lowercase if provided."""
        pet = PetUpdate(pet_type="DOG")
        assert pet.pet_type == "dog"

    def test_name_whitespace_stripping(self) -> None:
        """Test that name whitespace is stripped if provided."""
        pet = PetUpdate(name="  Buddy  ")
        assert pet.name == "Buddy"

    def test_empty_name_validation(self) -> None:
        """Test that empty names are rejected if provided."""
        with pytest.raises(ValidationError) as exc_info:
            PetUpdate(name="")
        # Pydantic returns "string should have at least 1 character" for empty strings
        assert "at least 1 character" in str(exc_info.value).lower()

        with pytest.raises(ValidationError) as exc_info:
            PetUpdate(name="   ")
        # Whitespace gets stripped, resulting in the same error
        assert (
            "at least 1 character" in str(exc_info.value).lower()
            or "whitespace" in str(exc_info.value).lower()
        )

    def test_none_values_allowed(self) -> None:
        """Test that None values are allowed for optional fields."""
        pet = PetUpdate(name=None, pet_type=None)
        assert pet.name is None
        assert pet.pet_type is None

    def test_pet_type_none_passthrough(self) -> None:
        """Test that None pet_type is not lowercased."""
        pet = PetUpdate(pet_type=None)
        assert pet.pet_type is None


class TestPetResponse:
    """Tests for PetResponse schema."""

    def test_from_orm_model(self) -> None:
        """Test creating PetResponse from ORM model."""
        from datetime import datetime

        # Create a mock ORM object
        class MockPet:
            id = 1
            name = "Buddy"
            pet_type = "dog"
            created_at = datetime(2024, 1, 1, 12, 0, 0)

        pet_response = PetResponse.model_validate(MockPet())
        assert pet_response.id == 1
        assert pet_response.name == "Buddy"
        assert pet_response.pet_type == "dog"
        assert pet_response.created_at == datetime(2024, 1, 1, 12, 0, 0)

    def test_id_validation(self) -> None:
        """Test that ID must be positive."""
        from datetime import datetime

        with pytest.raises(ValidationError) as exc_info:
            PetResponse(id=0, name="Buddy", pet_type="dog", created_at=datetime.now())
        assert "greater than or equal to 1" in str(exc_info.value).lower()

    def test_json_schema_example(self) -> None:
        """Test that JSON schema example is provided."""
        schema = PetResponse.model_json_schema()
        assert "example" in schema
        example = schema["example"]
        assert example["name"] == "Buddy"
        assert example["pet_type"] == "dog"
