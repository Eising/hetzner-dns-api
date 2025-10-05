"""DNS Record API view."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import override
import httpx
from loguru import logger
from .base import BaseApiView
from .types import (
    DnsBulkRecordCreateResponse,
    DnsBulkRecordUpdateResponse,
    DnsRecordBulkCreateRequest,
    DnsRecordBulkUpdateRequest,
    DnsRecordRequest,
    DnsRecordResponse,
    DnsRecordListResponse,
    DnsRecordItemResponse,
    DnsRecordUpdateRequest,
    RecordTypeCreatable,
)

from .decoding import decode_object, encode_object

logger.disable("hetzner_dns_api")

__docformat__ = "google"


class DnsBulkUpdateRecord(BaseApiView):
    """DNS Bulk Update handler."""

    @override
    def __init__(self, client: httpx.Client) -> None:
        """Create instance.

        @private
        """
        super().__init__(client)
        self.records: DnsRecordBulkUpdateRequest = DnsRecordBulkUpdateRequest()

    def add(
        self,
        record_id: str,
        zone_id: str,
        name: str,
        record_type: str,
        value: str,
        ttl: int | None = None,
    ) -> None:
        """Add a record to be updated.

        Args:
            record_id: The ID of the record
            zone_id: The ID of the parent zone
            name: The record name (e.g., www)
            record_type: A valid record type string e.g., A, AAAA or CNAME
            value: The value/content of the record e.g., an IP address
            ttl: Optional TTL value for the record. Defaults to the zone default TTL.
        """
        record_type = RecordTypeCreatable(record_type)
        record = DnsRecordUpdateRequest(
            id=record_id,
            zone_id=zone_id,
            name=name,
            value=value,
            type=record_type,
            ttl=ttl,
        )
        self.records.records.append(record)

    def submit(self) -> DnsBulkRecordUpdateResponse:
        """Submit the records for creation.

        This sends all entries that were added with the `add()` method in a
        single API request.

        Returns:
            `hetzner_dns_api.types.DnsBulkRecordUpdateResponse`
              This contains a list of valid and invalid updates.

        """
        body = encode_object(self.records)
        response = self._client.put(
            "/records/bulk", headers={"Content-Type": "application/json"}, content=body
        )
        self._validate_response(response)
        return decode_object(response.text, type=DnsBulkRecordUpdateResponse)


class DnsBulkCreateRecord(BaseApiView):
    """DNS Bulk Create Handler."""

    @override
    def __init__(self, client: httpx.Client) -> None:
        """Create instance.

        @private
        """
        super().__init__(client)
        self.records: DnsRecordBulkCreateRequest = DnsRecordBulkCreateRequest()

    def add(
        self,
        zone_id: str,
        name: str,
        record_type: str,
        value: str,
        ttl: int | None = None,
    ) -> None:
        """Add a record for creation.

        Args:
            zone_id: The ID of the parent zone
            name: The record name (e.g., www)
            record_type: A valid record type string e.g., A, AAAA or CNAME
            value: The value/content of the record e.g., an IP address
            ttl: Optional TTL value for the record. Defaults to the zone default TTL.
        """
        record_type = RecordTypeCreatable(record_type)
        record = DnsRecordRequest(
            zone_id=zone_id, name=name, value=value, type=record_type, ttl=ttl
        )
        self.records.records.append(record)

    def submit(self) -> DnsBulkRecordCreateResponse:
        """Submit the records for creation.

        This sends all entries that were added with the `add()` method in a
        single API request.

        Returns:
            `hetzner_dns_api.types.DnsBulkRecordCreateResponse`
              This contains a list of valid and invalid entries in the request.

        """
        body = encode_object(self.records)
        response = self._client.post(
            "/records/bulk", headers={"Content-Type": "application/json"}, content=body
        )
        self._validate_response(response)
        return decode_object(response.text, type=DnsBulkRecordCreateResponse)


class DnsRecord(BaseApiView):
    """DNS Record API view."""

    def all(self, zone_id: str) -> Iterator[DnsRecordResponse]:
        """Iterate all records.

        Args:
            zone_id: The ID string of the zone

        Yields:
            `hetzner_dns_api.types.DnsRecordResponse`

        """
        response = self._client.get("/records", params={"zone_id": zone_id})
        self._validate_response(response)
        logger.opt(lazy=True).debug(response.text)
        records = decode_object(response.text, type=DnsRecordListResponse)
        for record in records.records:
            yield record

    def get(self, record_id: str) -> DnsRecordResponse:
        """Get a single record.

        Args:
            record_id: The ID of the record.

        Returns:
            `hetzner_dns_api.types.DnsRecordResponse`
        """
        path = f"/records/{record_id}"
        response = self._client.get(path)
        self._validate_response(response)
        data = decode_object(response.text, type=DnsRecordItemResponse)
        return data.record

    def create(
        self,
        zone_id: str,
        name: str,
        record_type: str,
        value: str,
        ttl: int | None = None,
    ) -> DnsRecordResponse:
        """Create a record.

        Args:
            zone_id: The ID of the parent zone
            name: The record name (e.g., www)
            record_type: A valid record type string e.g., A, AAAA or CNAME
            value: The value/content of the record e.g., an IP address
            ttl: Optional TTL value for the record. Defaults to the zone default TTL.

        Returns:
            `hetzner_dns_api.types.DnsRecordResponse`
        """
        record_type = RecordTypeCreatable(record_type)
        request = DnsRecordRequest(
            zone_id=zone_id, name=name, value=value, type=record_type, ttl=ttl
        )
        body = encode_object(request)
        response = self._client.post(
            "/records", headers={"Content-Type": "application/json"}, content=body
        )
        self._validate_response(response)
        data = decode_object(response.text, type=DnsRecordItemResponse)
        return data.record

    def update(
        self,
        record_id: str,
        zone_id: str,
        name: str,
        record_type: str,
        value: str,
        ttl: int | None = None,
    ) -> DnsRecordResponse:
        """Update record.

        Args:
            record_id: The ID of the record to update
            zone_id: The ID of the parent zone
            name: The record name (e.g., www)
            record_type: A valid record type string e.g., A, AAAA or CNAME
            value: The value/content of the record e.g., an IP address
            ttl: Optional TTL value for the record. Defaults to the zone default TTL.

        Returns:
            `hetzner_dns_api.types.DnsRecordResponse`

        """
        path = f"/records/{record_id}"
        record_type = RecordTypeCreatable(record_type)
        request = DnsRecordRequest(
            zone_id=zone_id, name=name, value=value, type=record_type, ttl=ttl
        )
        body = encode_object(request)
        response = self._client.put(
            path, headers={"Content-Type": "application/json"}, content=body
        )
        self._validate_response(response)
        data = decode_object(response.text, type=DnsRecordItemResponse)
        return data.record

    def delete(self, record_id: str) -> None:
        """Delete a record."""
        path = f"/records/{record_id}"
        response = self._client.delete(path)
        self._validate_response(response)

    @contextmanager
    def bulk_create(self) -> Iterator[DnsBulkCreateRecord]:
        """Start a bulk creation context.

        This instantiates a context manager that allows you to create multiple
        records in a single API request.
        """
        manager = DnsBulkCreateRecord(self._client)
        yield manager

    @contextmanager
    def bulk_update(self) -> Iterator[DnsBulkUpdateRecord]:
        """Start a bulk update context.

        This instantiates a context manager that allows you to update multiple
        records in a single API request.
        """
        manager = DnsBulkUpdateRecord(self._client)
        yield manager
