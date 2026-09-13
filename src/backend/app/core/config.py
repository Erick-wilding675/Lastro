from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração do Lastro. Lê do .env — nunca hardcode credencial."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    neo4j_database: str = "neo4j"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    # Previews da Vercel nascem com hostname novo a cada deploy; listar um a um
    # não escala. O regex cobre o projeto inteiro sem abrir a API para todo mundo.
    cors_origin_regex: str = r"https://.*\.vercel\.app"

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
