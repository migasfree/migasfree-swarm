from pydantic import BaseModel, field_validator


VALIDITY_DAYS = 7305


class TokenCreateRequest(BaseModel):
    common_name: str
    validity_days: int = VALIDITY_DAYS

    @field_validator("validity_days")
    @classmethod
    def validate_validity_days(cls, v: int) -> int:
        if not 1 <= v <= VALIDITY_DAYS:
            raise ValueError(f"validity_days must be between 1 and {VALIDITY_DAYS}")

        return v


class TokenComputerRequest(BaseModel):
    uuid: str
    project_name: str
    validity_days: int = VALIDITY_DAYS
    username: str | None = None
    password: str | None = None

    @field_validator("validity_days")
    @classmethod
    def validate_validity_days(cls, v: int) -> int:
        if not 1 <= v <= VALIDITY_DAYS:
            raise ValueError(f"validity_days must be between 1 and {VALIDITY_DAYS}")
        return v


class TokenAdminResponse(BaseModel):
    url: str


class TokenComputerResponse(BaseModel):
    token: str


# Force explicit rebuild. Important!
TokenCreateRequest.model_rebuild()
TokenComputerRequest.model_rebuild()
TokenAdminResponse.model_rebuild()
TokenComputerResponse.model_rebuild()
