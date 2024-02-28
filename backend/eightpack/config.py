from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    DB_URL: str = "postgresql+psycopg2://user:password@localhost/dev"
    JWT_ISSUER: str = "8pack"
    DEBUG: bool = True
    JWT_KEY: str = "c827c6f28ccb356fcbfd2699"
    JWT_ALGO: str = "HS256"
    PROJECT_HOST: str = "0.0.0.0"
    PROJECT_PORT: int = 8003

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.DEBUG:
            sensitive_keys = ["JWT_KEY"]
            bad_keys = [
                c for c in sensitive_keys if getattr(self, c, None) == getattr(self.__class__, c, None)
            ]
            if bad_keys:
                raise ValueError(f"Keys have to be overridden (use EnvVars): {bad_keys}")


app_config = AppConfig()
