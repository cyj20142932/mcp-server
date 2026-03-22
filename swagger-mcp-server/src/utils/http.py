"""HTTP client utilities."""
import requests
from typing import Any


class HttpClient:
    """HTTP client with authentication support."""

    def __init__(self, auth_type: str = "none", auth_config: dict | None = None):
        self.auth_type = auth_type
        self.auth_config = auth_config or {}
        self.session = requests.Session()

    def prepare_headers(self, extra_headers: dict | None = None) -> dict:
        """Prepare request headers with authentication."""
        headers = {}

        # Add auth headers
        if self.auth_type == "bearer":
            token = self.auth_config.get("token", "")
            if token:
                headers["Authorization"] = f"Bearer {token}"

        elif self.auth_type == "apikey":
            api_key = self.auth_config.get("key", "")
            key_name = self.auth_config.get("key_name", "X-API-Key")
            location = self.auth_config.get("in", "header")

            if location == "header" and api_key:
                headers[key_name] = api_key

        elif self.auth_type == "basic":
            username = self.auth_config.get("username", "")
            password = self.auth_config.get("password", "")
            if username:
                from requests.auth import HTTPBasicAuth
                self.session.auth = HTTPBasicAuth(username, password)

        # Add extra headers
        if extra_headers:
            headers.update(extra_headers)

        return headers

    def prepare_params(self, params: dict | None = None) -> dict:
        """Prepare query parameters with API key if needed."""
        if not params:
            params = {}

        if self.auth_type == "apikey":
            api_key = self.auth_config.get("key", "")
            key_name = self.auth_config.get("key_name", "X-API-Key")
            location = self.auth_config.get("in", "header")

            if location == "query" and api_key:
                params[key_name] = api_key

        return params

    def request(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        data: Any = None,
        json: Any = None,
        headers: dict | None = None,
        timeout: int = 30,
    ) -> requests.Response:
        """Make HTTP request."""
        headers = self.prepare_headers(headers)
        params = self.prepare_params(params)

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            timeout=timeout,
        )
        return response


def build_url(base_url: str, path: str) -> str:
    """Build full URL from base and path."""
    base = base_url.rstrip("/")
    path = path.lstrip("/")
    return f"{base}/{path}"