"""Base API class."""

import abc
import httpx


class HetznerApiError(Exception):
    """Base hetzner API error."""


class HetznerApiNotFoundError(HetznerApiError):
    """Exception for when an item is not found."""


class AuthorizationFailedError(HetznerApiError):
    """Exception raised when authorization failed."""


class BaseApiView(abc.ABC):
    """Base API View class."""

    def __init__(self, client: httpx.Client) -> None:
        """Create api view handler."""
        self.client: httpx.Client = client

    def _validate_response(self, response: httpx.Response) -> None:
        """Validate response."""
        if response.status_code == 404:
            path = response.request.url.path
            raise HetznerApiNotFoundError(f"Item at {path} was not found.")
        if response.status_code == 401:
            raise AuthorizationFailedError(
                "API authorization failed. Please verify that the API key is correct."
            )

        if response.status_code not in (200, 201, 204):
            raise HetznerApiError(
                f"HTTP Error {response.status_code} received from Hetzner API: {response.text}"
            )
