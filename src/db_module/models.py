from typing import Any, Optional, Self
from sqlmodel import SQLModel, Field
from pydantic import model_validator


class DbConnParams(SQLModel):
    engine: str
    driver: Optional[str] = Field(default=None)
    host: Optional[str] = Field(default=None)
    port: Optional[int] = Field(default=None)
    username: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    params: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def check_field(self) -> Self:
        if self.engine == "sqlite":
            if not self.name:
                return self

            if not self.name.endswith(".db"):
                raise ValueError("Sqlite DB files should end with .db")

            return self

        errors = []
        errors.append("driver") if not self.driver else None
        errors.append("host") if not self.host else None
        errors.append("port") if not self.port else None
        errors.append("username") if not self.username else None
        errors.append("password") if not self.password else None
        errors.append("name") if not self.name else None

        if len(errors) != 0:
            raise ValueError("Required Fields Missing: " + ", ".join(errors))

        return self

    def __str__(self):
        sqlite = f"{self.engine}://" + (f"/{self.name}" if self.name else "")
        server = f"{self.engine}+{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"
        main_str = sqlite if self.engine == "sqlite" else server
        params = None if len(self.params) == 0 else "&".join([f"{k}={v}" for k, v in self.params.items()])

        return main_str + ("" if params is None else f"?{params}")
