from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime


class TokenCreateRequest(BaseModel):
    common_name: str           # CN solicitado
    validity_days: int = 7305  # Días de validez del certificado

    @field_validator('validity_days')
    @classmethod
    def validate_validity_days(cls, v: int) -> int:
        if not 1 <= v <= 7305:
            raise ValueError('validity_days must be between 1 and 7305')
        return v


class TokenCreateResponse(BaseModel):
    url: str
