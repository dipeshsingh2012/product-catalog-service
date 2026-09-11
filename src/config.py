import urllib.parse
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DATABASE_URL: str = Field(
        default="",
        validation_alias=AliasChoices("DATABASE_URL", "SQL_DB", "database_url", "sql_db"),
        description="PostgreSQL Neon database connection URL",
    )
    CORS_ORIGINS: list[str] = ["*"]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        if not v:
            return v

        # Automatically rewrite standard PostgreSQL schemes for SQLAlchemy asyncpg
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)

        # Parse query parameters to ensure asyncpg compatibility
        parsed = urllib.parse.urlsplit(v)
        if parsed.query:
            qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
            # 1. asyncpg expects 'ssl' parameter instead of 'sslmode'
            if "sslmode" in qs:
                ssl_vals = qs.pop("sslmode")
                if "ssl" not in qs:
                    qs["ssl"] = ssl_vals
            # 2. Strip libpq-specific parameters unsupported by asyncpg
            for unsupported in ["channel_binding", "gssencmode"]:
                qs.pop(unsupported, None)
            new_query = urllib.parse.urlencode(qs, doseq=True)
            v = urllib.parse.urlunsplit(parsed._replace(query=new_query))

        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()

