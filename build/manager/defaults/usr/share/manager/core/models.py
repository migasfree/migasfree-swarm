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


class BuildMGImageRequest(BaseModel):
    release_id: int


class BuildMGImageResponse(BaseModel):
    task_id: str


class BuildMCSISORequest(BaseModel):
    server_url: str | None = None
    server_ip: str | None = None
    keymap: str | None = None


class BuildMCSISOResponse(BaseModel):
    task_id: str


class BuildTaskStatus(BaseModel):
    task_id: str
    status: str  # queued|building|exporting|partitioning|installing|dumping|finalizing|completed|error
    progress: int = 0  # 0-100
    message: str = ""
    created_at: str | None = None
    updated_at: str | None = None


class BuildTaskLogsResponse(BaseModel):
    task_id: str
    logs: list[str]
    next_start: int


# Force explicit rebuild. Important!
TokenCreateRequest.model_rebuild()
TokenComputerRequest.model_rebuild()
TokenAdminResponse.model_rebuild()
TokenComputerResponse.model_rebuild()
BuildMGImageRequest.model_rebuild()
BuildMGImageResponse.model_rebuild()
BuildMCSISORequest.model_rebuild()
BuildMCSISOResponse.model_rebuild()
BuildTaskStatus.model_rebuild()
BuildTaskLogsResponse.model_rebuild()


