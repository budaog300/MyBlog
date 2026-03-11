from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsDB(BaseSettings):  
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET: str
    ALGORITHM: str

    model_config = SettingsConfigDict(env_file='.env')

    @property
    def get_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def get_auth_data(self) -> dict:
        return {"access_secret_key": self.JWT_SECRET_KEY, "refresh_secret_key": self.JWT_REFRESH_SECRET, "algorithm": self.ALGORITHM}
    

settings = SettingsDB()