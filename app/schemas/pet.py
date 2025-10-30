"""Pydantic schemas for Pet API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PetBase(BaseModel):
    """Base schema for Pet with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the pet",
        examples=["Buddy", "Whiskers"],
    )
    pet_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Type/species of the pet",
        examples=["dog", "cat", "bird"],
    )

    @field_validator("name", "pet_type")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure fields are not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or just whitespace")
        return v.strip()

    @field_validator("pet_type")
    @classmethod
    def lowercase_pet_type(cls, v: str) -> str:
        """Convert pet type to lowercase for consistency."""
        return v.lower()


class PetCreate(PetBase):
    """Schema for creating a new pet."""

    pass


class PetUpdate(BaseModel):
    """Schema for updating an existing pet."""

    name: str | None = Field(
        None, min_length=1, max_length=100, description="Updated name of the pet"
    )
    pet_type: str | None = Field(
        None, min_length=1, max_length=50, description="Updated type/species of the pet"
    )

    model_config = ConfigDict(validate_assignment=True, str_strip_whitespace=True)

    @field_validator("name", "pet_type")
    @classmethod
    def validate_not_empty_if_provided(cls, v: str | None) -> str | None:
        """Ensure fields are not just whitespace if provided."""
        if v is not None:
            if not v.strip():
                raise ValueError("Field cannot be empty or just whitespace")
            return v.strip()
        return v

    @field_validator("pet_type")
    @classmethod
    def lowercase_pet_type_if_provided(cls, v: str | None) -> str | None:
        """Convert pet type to lowercase if provided."""
        return v.lower() if v else v


class PetResponse(PetBase):
    """Schema for Pet response with all fields."""

    id: int = Field(..., description="Unique identifier for the pet", ge=1)
    created_at: datetime = Field(..., description="Timestamp when pet was registered")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Buddy",
                "pet_type": "dog",
                "created_at": "2024-01-01T12:00:00",
            }
        },
    )


class PetList(BaseModel):
    """Schema for list of pets response."""

    items: list[PetResponse] = Field(..., description="List of pets")
    total: int = Field(..., description="Total number of pets", ge=0)
    skip: int = Field(default=0, description="Number of items skipped", ge=0)
    limit: int = Field(
        default=100, description="Maximum number of items returned", ge=1
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "name": "Buddy",
                        "pet_type": "dog",
                        "created_at": "2024-01-01T12:00:00",
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100,
            }
        }
    )
