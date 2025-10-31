"""Tests for database models."""

from datetime import datetime

import pytest

from app.models.pet import Pet


class TestPetModel:
    """Tests for Pet model methods."""

    def test_pet_repr(self) -> None:
        """Test __repr__ method."""
        pet = Pet(id=1, name="Buddy", pet_type="dog")
        repr_str = repr(pet)

        assert "Pet" in repr_str
        assert "id=1" in repr_str
        assert "name='Buddy'" in repr_str
        assert "type='dog'" in repr_str

    def test_pet_str(self) -> None:
        """Test __str__ method."""
        pet = Pet(id=1, name="Whiskers", pet_type="cat")
        str_result = str(pet)

        assert str_result == "Whiskers (cat)"

    def test_pet_to_dict_with_created_at(self) -> None:
        """Test to_dict method with created_at."""
        now = datetime.now()
        pet = Pet(id=1, name="Tweety", pet_type="bird", created_at=now)
        pet_dict = pet.to_dict()

        assert pet_dict["id"] == 1
        assert pet_dict["name"] == "Tweety"
        assert pet_dict["pet_type"] == "bird"
        assert pet_dict["created_at"] == now.isoformat()

    def test_pet_to_dict_without_created_at(self) -> None:
        """Test to_dict method when created_at is None."""
        pet = Pet(id=1, name="Buddy", pet_type="dog")
        pet.created_at = None  # type: ignore[assignment]
        pet_dict = pet.to_dict()

        assert pet_dict["id"] == 1
        assert pet_dict["name"] == "Buddy"
        assert pet_dict["pet_type"] == "dog"
        assert pet_dict["created_at"] is None
