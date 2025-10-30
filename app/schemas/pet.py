from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    pet_type: str = Field(..., min_length=1, max_length=50)


class PetCreate(PetBase):
    pass


class PetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    pet_type: Optional[str] = Field(None, min_length=1, max_length=50)


class PetResponse(PetBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True