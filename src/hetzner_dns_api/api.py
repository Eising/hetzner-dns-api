"""Main DNS api."""

import httpx

from .zone import DnsZone
from .records import DnsRecord

__docformat__ = "google"

BASE_API_URL = "https://dns.hetzner.com/api/v1"

class HetznerDNS:
    """Hetzner DNS API client."""

    def __init__(self, auth_api_token: str) -> None:
        """Initialize API client."""
        self._client: httpx.Client = httpx.Client(
            base_url=BASE_API_URL, headers={"Auth-API-Token": auth_api_token}
        )

        self._zones: DnsZone = DnsZone(self._client)
        self._records: DnsRecord = DnsRecord(self._client)

    @property
    def zones(self) -> DnsZone:
        """Manage DNS Zones.

        This provides an initialized instance of the `DnsZone` class and can be
        used to manage DNS zones.
        """
        return self._zones

    @property
    def records(self) -> DnsRecord:
        """Manage DNS Records.

        This provides an initialized instance of the `DnsRecord` class and can
        be used to manage DNS entries in your zones.
        """
        return self._records
