"""Tests for pet API endpoints."""

from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pet import Pet


@pytest.mark.asyncio
class TestPetCreate:
    """Tests for pet creation endpoint."""
    
    async def test_create_pet_success(
        self, client: AsyncClient, sample_pet_data: dict[str, Any]
    ) -> None:
        """Test successful pet creation."""
        response = await client.post("/api/pets/", json=sample_pet_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_pet_data["name"]
        assert data["pet_type"] == sample_pet_data["pet_type"]
        assert "id" in data
        assert "created_at" in data
    
    async def test_create_pet_lowercase_type(self, client: AsyncClient) -> None:
        """Test that pet type is converted to lowercase."""
        pet_data = {"name": "Rex", "pet_type": "DOG"}
        response = await client.post("/api/pets/", json=pet_data)
        
        assert response.status_code == 201
        assert response.json()["pet_type"] == "dog"
    
    async def test_create_pet_missing_name(self, client: AsyncClient) -> None:
        """Test pet creation with missing name."""
        response = await client.post("/api/pets/", json={"pet_type": "dog"})
        
        assert response.status_code == 422
        assert "name" in response.text.lower()
    
    async def test_create_pet_missing_type(self, client: AsyncClient) -> None:
        """Test pet creation with missing type."""
        response = await client.post("/api/pets/", json={"name": "Buddy"})
        
        assert response.status_code == 422
        assert "pet_type" in response.text.lower()
    
    async def test_create_pet_empty_name(self, client: AsyncClient) -> None:
        """Test pet creation with empty name."""
        response = await client.post("/api/pets/", json={"name": "", "pet_type": "dog"})
        
        assert response.status_code == 422
    
    async def test_create_pet_whitespace_name(self, client: AsyncClient) -> None:
        """Test that whitespace-only names are rejected."""
        response = await client.post("/api/pets/", json={"name": "   ", "pet_type": "dog"})
        
        assert response.status_code == 422


@pytest.mark.asyncio
class TestPetList:
    """Tests for pet listing endpoint."""
    
    async def test_list_pets_empty(self, client: AsyncClient) -> None:
        """Test listing pets when database is empty."""
        response = await client.get("/api/pets/")
        
        assert response.status_code == 200
        assert response.json() == []
    
    async def test_list_pets_with_data(
        self, client: AsyncClient, sample_pets_data: list[dict[str, Any]]
    ) -> None:
        """Test listing pets with data."""
        # Create multiple pets
        for pet_data in sample_pets_data:
            await client.post("/api/pets/", json=pet_data)
        
        # List all pets
        response = await client.get("/api/pets/")
        
        assert response.status_code == 200
        pets = response.json()
        assert len(pets) == len(sample_pets_data)
        
        # Check pets are ordered by created_at desc (newest first)
        for i in range(len(pets) - 1):
            assert pets[i]["created_at"] >= pets[i + 1]["created_at"]
    
    async def test_list_pets_pagination(
        self, client: AsyncClient, sample_pets_data: list[dict[str, Any]]
    ) -> None:
        """Test pagination parameters."""
        # Create multiple pets
        for pet_data in sample_pets_data:
            await client.post("/api/pets/", json=pet_data)
        
        # Test with skip and limit
        response = await client.get("/api/pets/?skip=1&limit=2")
        
        assert response.status_code == 200
        pets = response.json()
        assert len(pets) == 2
    
    async def test_list_pets_filter_by_type(
        self, client: AsyncClient, sample_pets_data: list[dict[str, Any]]
    ) -> None:
        """Test filtering pets by type."""
        # Create multiple pets
        for pet_data in sample_pets_data:
            await client.post("/api/pets/", json=pet_data)
        
        # Filter by dog type
        response = await client.get("/api/pets/?pet_type=dog")
        
        assert response.status_code == 200
        pets = response.json()
        assert all(pet["pet_type"] == "dog" for pet in pets)
        assert len(pets) == 2  # Based on sample data
    
    async def test_list_pets_invalid_pagination(self, client: AsyncClient) -> None:
        """Test invalid pagination parameters."""
        response = await client.get("/api/pets/?skip=-1")
        assert response.status_code == 422
        
        response = await client.get("/api/pets/?limit=0")
        assert response.status_code == 422
        
        response = await client.get("/api/pets/?limit=1001")
        assert response.status_code == 422


@pytest.mark.asyncio
class TestPetGet:
    """Tests for getting a specific pet."""
    
    async def test_get_pet_success(
        self, client: AsyncClient, sample_pet_data: dict[str, Any]
    ) -> None:
        """Test getting an existing pet."""
        # Create a pet
        create_response = await client.post("/api/pets/", json=sample_pet_data)
        pet_id = create_response.json()["id"]
        
        # Get the pet
        response = await client.get(f"/api/pets/{pet_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pet_id
        assert data["name"] == sample_pet_data["name"]
        assert data["pet_type"] == sample_pet_data["pet_type"]
    
    async def test_get_pet_not_found(self, client: AsyncClient) -> None:
        """Test getting a non-existent pet."""
        response = await client.get("/api/pets/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_get_pet_invalid_id(self, client: AsyncClient) -> None:
        """Test getting a pet with invalid ID."""
        response = await client.get("/api/pets/0")
        assert response.status_code == 422
        
        response = await client.get("/api/pets/abc")
        assert response.status_code == 422


@pytest.mark.asyncio
class TestPetUpdate:
    """Tests for pet update endpoint."""
    
    async def test_update_pet_name(
        self, client: AsyncClient, sample_pet_data: dict[str, Any]
    ) -> None:
        """Test updating pet name."""
        # Create a pet
        create_response = await client.post("/api/pets/", json=sample_pet_data)
        pet_id = create_response.json()["id"]
        
        # Update the name
        update_data = {"name": "New Name"}
        response = await client.put(f"/api/pets/{pet_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["pet_type"] == sample_pet_data["pet_type"]  # Unchanged
    
    async def test_update_pet_type(
        self, client: AsyncClient, sample_pet_data: dict[str, Any]
    ) -> None:
        """Test updating pet type."""
        # Create a pet
        create_response = await client.post("/api/pets/", json=sample_pet_data)
        pet_id = create_response.json()["id"]
        
        # Update the type
        update_data = {"pet_type": "cat"}
        response = await client.put(f"/api/pets/{pet_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["pet_type"] == "cat"
        assert data["name"] == sample_pet_data["name"]  # Unchanged
    
    async def test_update_pet_both_fields(
        self, client: AsyncClient, sample_pet_data: dict[str, Any]
    ) -> None:
        """Test updating both name and type."""
        # Create a pet
        create_response = await client.post("/api/pets/", json=sample_pet_data)
        pet_id = create_response.json()["id"]
        
        # Update both fields
        update_data = {"name": "Max", "pet_type": "hamster"}
        response = await client.put(f"/api/pets/{pet_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Max"
        assert data["pet_type"] == "hamster"
    
    async def test_update_pet_empty_request(
        self, client: AsyncClient, sample_pet_data: dict[str, Any]
    ) -> None:
        """Test update with empty request body."""
        # Create a pet
        create_response = await client.post("/api/pets/", json=sample_pet_data)
        pet_id = create_response.json()["id"]
        original_data = create_response.json()
        
        # Update with empty body
        response = await client.put(f"/api/pets/{pet_id}", json={})
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == original_data["name"]
        assert data["pet_type"] == original_data["pet_type"]
    
    async def test_update_pet_not_found(self, client: AsyncClient) -> None:
        """Test updating a non-existent pet."""
        update_data = {"name": "New Name"}
        response = await client.put("/api/pets/999", json=update_data)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_update_pet_invalid_name(
        self, client: AsyncClient, sample_pet_data: dict[str, Any]
    ) -> None:
        """Test update with invalid name."""
        # Create a pet
        create_response = await client.post("/api/pets/", json=sample_pet_data)
        pet_id = create_response.json()["id"]
        
        # Try to update with empty name
        response = await client.put(f"/api/pets/{pet_id}", json={"name": ""})
        assert response.status_code == 422
        
        # Try to update with whitespace name
        response = await client.put(f"/api/pets/{pet_id}", json={"name": "   "})
        assert response.status_code == 422


@pytest.mark.asyncio
class TestPetDelete:
    """Tests for pet deletion endpoint."""
    
    async def test_delete_pet_success(
        self, client: AsyncClient, sample_pet_data: dict[str, Any]
    ) -> None:
        """Test successful pet deletion."""
        # Create a pet
        create_response = await client.post("/api/pets/", json=sample_pet_data)
        pet_id = create_response.json()["id"]
        
        # Delete the pet
        response = await client.delete(f"/api/pets/{pet_id}")
        
        assert response.status_code == 204
        assert response.content == b""
        
        # Verify pet is deleted
        get_response = await client.get(f"/api/pets/{pet_id}")
        assert get_response.status_code == 404
    
    async def test_delete_pet_not_found(self, client: AsyncClient) -> None:
        """Test deleting a non-existent pet."""
        response = await client.delete("/api/pets/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_delete_pet_invalid_id(self, client: AsyncClient) -> None:
        """Test deleting with invalid ID."""
        response = await client.delete("/api/pets/0")
        assert response.status_code == 422
        
        response = await client.delete("/api/pets/abc")
        assert response.status_code == 422


@pytest.mark.asyncio
class TestPetStats:
    """Tests for pet statistics endpoint."""
    
    async def test_stats_empty_database(self, client: AsyncClient) -> None:
        """Test statistics with empty database."""
        response = await client.get("/api/pets/stats/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_pets"] == 0
        assert data["pets_by_type"] == {}
    
    async def test_stats_with_data(
        self, client: AsyncClient, sample_pets_data: list[dict[str, Any]]
    ) -> None:
        """Test statistics with pets in database."""
        # Create multiple pets
        for pet_data in sample_pets_data:
            await client.post("/api/pets/", json=pet_data)
        
        # Get statistics
        response = await client.get("/api/pets/stats/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_pets"] == 5
        assert data["pets_by_type"]["dog"] == 2
        assert data["pets_by_type"]["cat"] == 2
        assert data["pets_by_type"]["bird"] == 1


@pytest.mark.asyncio
class TestDatabaseErrorHandling:
    """Tests for database error handling in API endpoints."""

    async def test_create_pet_database_error(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test create pet handles database errors."""
        from sqlalchemy.exc import SQLAlchemyError
        from app.repositories.pet import PetRepository

        async def mock_create_error(*args, **kwargs):
            raise SQLAlchemyError("Database connection failed")

        monkeypatch.setattr(PetRepository, "create", mock_create_error)

        response = await client.post(
            "/api/pets/", json={"name": "Test", "pet_type": "dog"}
        )

        assert response.status_code == 500
        assert "database error" in response.json()["detail"].lower()

    async def test_create_pet_integrity_error(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test create pet handles integrity constraint violations."""
        from sqlalchemy.exc import IntegrityError
        from app.repositories.pet import PetRepository

        async def mock_create_integrity_error(*args, **kwargs):
            raise IntegrityError("", "", "")

        monkeypatch.setattr(PetRepository, "create", mock_create_integrity_error)

        response = await client.post(
            "/api/pets/", json={"name": "Test", "pet_type": "dog"}
        )

        assert response.status_code == 400
        assert "integrity" in response.json()["detail"].lower()

    async def test_list_pets_database_error(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test list pets handles database errors."""
        from sqlalchemy.exc import SQLAlchemyError
        from app.repositories.pet import PetRepository

        async def mock_get_multi_error(*args, **kwargs):
            raise SQLAlchemyError("Database connection failed")

        monkeypatch.setattr(PetRepository, "get_multi", mock_get_multi_error)

        response = await client.get("/api/pets/")

        assert response.status_code == 500
        assert "database error" in response.json()["detail"].lower()

    async def test_list_pets_by_type_database_error(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test list pets by type handles database errors."""
        from sqlalchemy.exc import SQLAlchemyError
        from app.repositories.pet import PetRepository

        async def mock_get_by_type_error(*args, **kwargs):
            raise SQLAlchemyError("Database connection failed")

        monkeypatch.setattr(PetRepository, "get_by_type", mock_get_by_type_error)

        response = await client.get("/api/pets/?pet_type=dog")

        assert response.status_code == 500
        assert "database error" in response.json()["detail"].lower()

    async def test_update_pet_integrity_error(
        self, client: AsyncClient, sample_pet_data: dict[str, Any], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test update pet handles integrity constraint violations."""
        from sqlalchemy.exc import IntegrityError
        from app.repositories.pet import PetRepository

        # Create a pet first
        create_response = await client.post("/api/pets/", json=sample_pet_data)
        pet_id = create_response.json()["id"]

        async def mock_update_integrity_error(*args, **kwargs):
            raise IntegrityError("", "", "")

        monkeypatch.setattr(PetRepository, "update", mock_update_integrity_error)

        response = await client.put(
            f"/api/pets/{pet_id}", json={"name": "Updated"}
        )

        assert response.status_code == 400
        assert "integrity" in response.json()["detail"].lower()

    async def test_update_pet_database_error(
        self, client: AsyncClient, sample_pet_data: dict[str, Any], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test update pet handles database errors."""
        from sqlalchemy.exc import SQLAlchemyError
        from app.repositories.pet import PetRepository

        # Create a pet first
        create_response = await client.post("/api/pets/", json=sample_pet_data)
        pet_id = create_response.json()["id"]

        async def mock_update_error(*args, **kwargs):
            raise SQLAlchemyError("Database connection failed")

        monkeypatch.setattr(PetRepository, "update", mock_update_error)

        response = await client.put(
            f"/api/pets/{pet_id}", json={"name": "Updated"}
        )

        assert response.status_code == 500
        assert "database error" in response.json()["detail"].lower()

    async def test_delete_pet_database_error(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test delete pet handles database errors."""
        from sqlalchemy.exc import SQLAlchemyError
        from app.repositories.pet import PetRepository

        async def mock_delete_error(*args, **kwargs):
            raise SQLAlchemyError("Database connection failed")

        monkeypatch.setattr(PetRepository, "delete", mock_delete_error)

        response = await client.delete("/api/pets/1")

        assert response.status_code == 500
        assert "failed to delete" in response.json()["detail"].lower()

    async def test_stats_database_error(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test stats endpoint handles database errors."""
        from sqlalchemy.exc import SQLAlchemyError
        from app.repositories.pet import PetRepository

        async def mock_count_error(*args, **kwargs):
            raise SQLAlchemyError("Database connection failed")

        monkeypatch.setattr(PetRepository, "count", mock_count_error)

        response = await client.get("/api/pets/stats/summary")

        assert response.status_code == 500
        assert "failed to retrieve statistics" in response.json()["detail"].lower()