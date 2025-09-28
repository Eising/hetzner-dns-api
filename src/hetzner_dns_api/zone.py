"""DNS Zone iterator."""

from collections.abc import Iterator
from typing import Self
import httpx
import json
import msgspec

from .types import (
    DnsZoneGetResponse,
    DnsZoneListResponse,
    DnsZoneResponse,
    DnsZoneValidationResponse,
    PageMeta,
)
from .base import HetznerApiError, BaseApiView
from .decoding import decode_object


class ZoneIterator:
    """Paged Response iterator.

    This allows you to pass in any httpx response from the API, and then be able
    to iterate page by page.

    """

    def __init__(
        self,
        client: httpx.Client,
        response: httpx.Response,
    ) -> None:
        """Create response page iterator."""
        self.response: httpx.Response = response
        self.client: httpx.Client = client
        self.current: list[DnsZoneResponse] = self.extract_content(response)

    def __iter__(self) -> Self:
        """Iterate."""
        return self

    def extract_meta(self, response: httpx.Response) -> PageMeta | None:
        """Extract metadata."""
        data = decode_object(response.text, DnsZoneListResponse)
        return data.meta.pagination

    def extract_content(self, response: httpx.Response) -> list[DnsZoneResponse]:
        """Extract content from response."""
        try:
            data = decode_object(response.text, DnsZoneListResponse)
        except msgspec.ValidationError as e:
            parsed_json = response.json()
            formatted_json = json.dumps(parsed_json, indent=2)
            raise HetznerApiError(
                f"Unable to parse response: {e}. Response:\n{formatted_json}"
            )
        return data.zones

    def resolve_query(self, response: httpx.Response) -> dict[str, str]:
        """Resolve the next query from existing response.."""
        query = dict(response.request.url.params)
        next_page = 2
        if page_num := query.get("page"):
            next_page = int(page_num) + 1

        query["page"] = str(next_page)

        return query

    def _build_next_request(self) -> httpx.Request:
        """Build next request."""
        params = self.resolve_query(self.response)
        current_request = self.response.request
        if str(self.client.base_url):
            next_url = str(current_request.url.path)
        else:
            next_url = str(current_request.url)
        request = self.client.build_request(
            method=current_request.method,
            url=next_url,
            params=params,
        )
        return request

    def can_iter(self, metadata: PageMeta) -> bool:
        """Check if we can iterate."""
        return metadata.page < metadata.last_page

    def __next__(self) -> DnsZoneResponse:
        """Get next response."""
        if not self.current:
            self.get_next()
        if self.current:
            return self.current.pop(0)
        raise StopIteration()

    def get_next(self) -> None:
        """Get rnext response."""
        metadata = self.extract_meta(self.response)
        if not metadata or not self.can_iter(metadata):
            return
        request = self._build_next_request()
        response = self.client.send(request)
        self.current = self.extract_content(response)
        self.response = response


class DnsZone(BaseApiView):
    """DNS Zone."""

    def count(self, zone_id: str) -> int:
        """Get a count of the records in a zone."""
        zone = self.get(zone_id)
        return zone.records_count

    def get_id(self, name: str) -> str | None:
        """Get the ID of a domain."""
        params: dict[str, str] = {"name": name}
        response = self.client.get("/zones", params=params)
        zones = decode_object(response.text, type=DnsZoneListResponse)
        if zones.zones:
            return zones.zones[0].id
        return None

    def all(
        self,
        name: str | None = None,
        search: bool = False,
    ) -> Iterator[DnsZoneResponse]:
        """Iterate all zones."""
        params: dict[str, str] = {}
        if name and not search:
            params["name"] = name
        elif name and search:
            params["search_name"] = name

        response = self.client.get("/zones", params=params)
        iterator = ZoneIterator(self.client, response)
        for result in iterator:
            yield result

    def create(self, name: str, ttl: int | None = None) -> DnsZoneResponse:
        """Create a zone."""
        params: dict[str, str | int] = {"name": name}
        if ttl:
            params["ttl"] = ttl
        response = self.client.post("/zones", params=params)
        self._validate_response(response)
        data = decode_object(response.text, DnsZoneGetResponse)
        return data.zone

    def get(self, zone_id: str) -> DnsZoneResponse:
        """Get a single zone by ID."""
        path = f"/zones/{zone_id}"
        response = self.client.get(path)
        self._validate_response(response)
        return decode_object(response.text, type=DnsZoneGetResponse).zone

    def update(
        self, zone_id: str, name: str, ttl: int | None = None
    ) -> DnsZoneResponse:
        """Update zone."""
        path = f"/zones/{zone_id}"
        body: dict[str, str | int] = {"name": name}
        if ttl:
            body["ttl"] = ttl

        response = self.client.put(path, json=body)
        self._validate_response(response)
        return decode_object(response.text, type=DnsZoneGetResponse).zone

    def delete(self, zone_id: str) -> None:
        """Delete a zone."""
        path = f"/zones/{zone_id}/import"
        response = self.client.delete(path)
        self._validate_response(response)

    def import_zone(self, zone_id: str, content: str) -> DnsZoneResponse:
        """Import zone from string."""
        path = f"/zones/{zone_id}"
        response = self.client.post(
            path, headers={"Content-Type": "text/plain"}, content=content
        )
        self._validate_response(response)

        return decode_object(response.text, type=DnsZoneGetResponse).zone

    def export_zone(self, zone_id: str) -> str:
        """Export a zone to a string."""
        path = f"/zones/{zone_id}/export"
        response = self.client.get(path)
        self._validate_response(response)
        return response.text

    def validate_zone(self, zone_id: str, content: str) -> DnsZoneValidationResponse:
        """Validate zone."""
        path = f"/zones/{zone_id}/validate"
        response = self.client.post(
            path, headers={"Content-Type": "text/plain"}, content=content
        )
        self._validate_response(response)
        return decode_object(response.text, type=DnsZoneValidationResponse)
