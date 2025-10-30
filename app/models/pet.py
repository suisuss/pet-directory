"""Pet model for database."""

from datetime import datetime
from typing import Any, ClassVar

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Pet(Base):
    """Pet model representing a pet in the directory."""

    __tablename__ = "pets"
    __table_args__: ClassVar = {"schema": None}  # type: ignore[misc]  # Use default schema

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        nullable=False,
        comment="Unique identifier for the pet",
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=False, comment="Name of the pet"
    )
    pet_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, comment="Type/species of the pet"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the pet was registered",
    )

    def __repr__(self) -> str:
        """String representation of the Pet model."""
        return f"<Pet(id={self.id}, name='{self.name}', type='{self.pet_type}')>"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.name} ({self.pet_type})"

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "pet_type": self.pet_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
