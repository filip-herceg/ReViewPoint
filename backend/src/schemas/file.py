
from datetime import datetime
from typing import Final
from pydantic import BaseModel, Field
from pydantic import ConfigDict


class FileSchema(BaseModel):
    """Schema for file metadata used in API requests and responses.

    Attributes:
        id (int): Unique identifier for the file.
        filename (str): Name of the file.
        content_type (str): MIME type of the file.
        user_id (int): ID of the user who owns the file.
        created_at (datetime): Timestamp when the file was created.
    """

    id: int = Field(..., description="Unique identifier for the file")
    filename: str = Field(..., max_length=255, description="Name of the file")
    content_type: str = Field(..., max_length=128, description="MIME type of the file")
    user_id: int = Field(..., description="ID of the user who owns the file")
    created_at: datetime = Field(..., description="Timestamp when the file was created")

    model_config = ConfigDict(from_attributes=True)
