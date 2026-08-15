from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    tenant_code: str = Field(min_length=1, max_length=32)
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)
    remember_me: bool = False
    captcha_id: str | None = Field(default=None, max_length=64)
    captcha_code: str | None = Field(default=None, max_length=16)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 0
    remember_me: bool = False


class MeOut(BaseModel):
    id: int
    tenant_id: int
    tenant_code: str = ""
    tenant_name: str | None = None
    logo_url: str | None = None
    username: str
    full_name: str | None
    is_superuser: bool
    roles: list[str]
    permissions: list[str]
