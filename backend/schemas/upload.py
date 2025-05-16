from pydantic import BaseModel, Field, ConfigDict


class UploadRequest(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "My Thesis"})
    author: str = Field(..., json_schema_extra={"example": "Jane Doe"})
    content: str = Field(
        ..., json_schema_extra={"example": "Base64-encoded PDF or plain text"}
    )

    model_config = ConfigDict(from_attributes=True)
