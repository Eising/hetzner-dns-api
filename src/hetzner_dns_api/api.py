"""Main DNS api."""

import httpx

from .zone import DnsZone
from .records import DnsRecord

BASE_API_URL = "https://dns.hetzner.com/api/v1"

class HetznerDNS:
    """Hetzner DNS API client."""

    def __init__(self, auth_api_token: str) -> None:
        """Initialize API client."""
        self.client: httpx.Client = httpx.Client(
            base_url=BASE_API_URL, headers={"Auth-API-Token": auth_api_token}
        )

        self._zones: DnsZone = DnsZone(self.client)
        self._records: DnsRecord = DnsRecord(self.client)

    @property
    def zones(self) -> DnsZone:
        """Manage DNS Zones."""
        return self._zones

    @property
    def records(self) -> DnsRecord:
        """Manage DNS Records. """
        return self._records
