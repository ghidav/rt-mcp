import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get project root directory (approximate based on this file location)
# this file is in src/rt_mcp/config.py, so root is ../../..
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class RTConfig(BaseSettings):
    """RT Server configuration from environment variables."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Required
    rt_url: str

    # Authentication (either token OR user+password)
    rt_token: str | None = None
    rt_user: str | None = None
    rt_password: str | None = None

    # Optional settings
    rt_timeout: int = 30
    rt_verify_ssl: bool = True
    rt_base_path: str = "/REST/2.0"

    def get_auth_header(self) -> dict[str, str]:
        """
        Generate authentication header based on available credentials.

        Returns:
            Dict with Authorization header

        Raises:
            ValueError: If neither token nor user+password are provided
        """
        if self.rt_token:
            return {"Authorization": f"token {self.rt_token}"}
        elif self.rt_user and self.rt_password:
            credentials = f"{self.rt_user}:{self.rt_password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            return {"Authorization": f"Basic {encoded}"}
        else:
            raise ValueError(
                "Either RT_TOKEN or both RT_USER and RT_PASSWORD must be set"
            )

    @property
    def base_url(self) -> str:
        """Full base URL for RT REST2 API."""
        url = self.rt_url.rstrip('/')
        if url.endswith(self.rt_base_path):
            return url
        return f"{url}{self.rt_base_path}"
