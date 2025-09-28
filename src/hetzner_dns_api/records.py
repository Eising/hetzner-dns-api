"""DNS Record API view."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import override
import httpx
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

class DnsBulkUpdateRecord(BaseApiView):
    """DNS Bulk Update handler."""

    @override
    def __init__(self, client: httpx.Client) -> None:
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
        """Add a record for update."""
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
        """Submit the records for creation."""
        body = encode_object(self.records)
        response = self.client.put(
            "/records/bulk", headers={"Content-Type": "application/json"}, content=body
        )
        self._validate_response(response)
        return decode_object(response.text, type=DnsBulkRecordUpdateResponse)


class DnsBulkCreateRecord(BaseApiView):
    """DNS Bulk Create Handler."""

    @override
    def __init__(self, client: httpx.Client) -> None:
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
        """Add a record for creation."""
        record_type = RecordTypeCreatable(record_type)
        record = DnsRecordRequest(
            zone_id=zone_id, name=name, value=value, type=record_type, ttl=ttl
        )
        self.records.records.append(record)

    def submit(self) -> DnsBulkRecordCreateResponse:
        """Submit the records for creation."""
        body = encode_object(self.records)
        response = self.client.post(
            "/records/bulk", headers={"Content-Type": "application/json"}, content=body
        )
        self._validate_response(response)
        return decode_object(response.text, type=DnsBulkRecordCreateResponse)


class DnsRecord(BaseApiView):
    """DNS Record API view."""

    def all(self, zone_id: str) -> Iterator[DnsRecordResponse]:
        """Iterate all records."""
        response = self.client.get("/records", params={"zone_id": zone_id})
        self._validate_response(response)
        records = decode_object(response.text, type=DnsRecordListResponse)
        for record in records.records:
            yield record

    def get(self, record_id: str) -> DnsRecordResponse:
        """Get record."""
        path = f"/records/{record_id}"
        response = self.client.get(path)
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
        """Create a record."""
        record_type = RecordTypeCreatable(record_type)
        request = DnsRecordRequest(
            zone_id=zone_id, name=name, value=value, type=record_type, ttl=ttl
        )
        body = encode_object(request)
        response = self.client.post(
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
        """Update record."""
        path = f"/records/{record_id}"
        record_type = RecordTypeCreatable(record_type)
        request = DnsRecordRequest(
            zone_id=zone_id, name=name, value=value, type=record_type, ttl=ttl
        )
        body = encode_object(request)
        response = self.client.put(
            path, headers={"Content-Type": "application/json"}, content=body
        )
        self._validate_response(response)
        data = decode_object(response.text, type=DnsRecordItemResponse)
        return data.record

    def delete(self, record_id: str) -> None:
        """Delete a record."""
        path = f"/records/{record_id}"
        response = self.client.delete(path)
        self._validate_response(response)

    @contextmanager
    def bulk_create(self) -> Iterator[DnsBulkCreateRecord]:
        """Start a bulk creation context."""
        manager = DnsBulkCreateRecord(self.client)
        yield manager

    @contextmanager
    def bulk_update(self) -> Iterator[DnsBulkUpdateRecord]:
        """Start a bulk update context."""
        manager = DnsBulkUpdateRecord(self.client)
        yield manager
