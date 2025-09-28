"""Tests for Zones."""

import pytest
from hetzner_dns_api.types import DnsRecordItemResponse, DnsRecordListResponse, DnsZoneGetResponse, DnsZoneListResponse
from hetzner_dns_api.decoding import decode_object

RESPONSE_ZONES_GET_ALL = """
{
  "zones": [
    {
      "id": "string",
      "created": "2025-09-26 13:18:19.838 +0000 UTC",
      "modified": "2025-09-26 13:18:19.838 +0000 UTC",
      "legacy_dns_host": "string",
      "legacy_ns": [
        "string"
      ],
      "name": "string",
      "ns": [
        "string"
      ],
      "owner": "string",
      "paused": true,
      "permission": "string",
      "project": "string",
      "registrar": "string",
      "status": "verified",
      "ttl": 0,
      "verified": "2025-09-26 13:18:19.838 +0000 UTC",
      "records_count": 0,
      "is_secondary_dns": true,
      "txt_verification": {
        "name": "string",
        "token": "string"
      }
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 1,
      "last_page": 1,
      "total_entries": 0
    }
  }
}
"""

REQUEST_ZONE_CREATE = """
{
  "name": "string",
  "ttl": 0
}
"""

RESPONSE_ZONE_CREATE = """
{
  "zone": {
    "id": "string",
    "created": "2025-09-26 13:18:19.838 +0000 UTC",
    "modified": "2025-09-26 13:18:19.838 +0000 UTC",
    "legacy_dns_host": "string",
    "legacy_ns": [
      "string"
    ],
    "name": "string",
    "ns": [
      "string"
    ],
    "owner": "string",
    "paused": true,
    "permission": "string",
    "project": "string",
    "registrar": "string",
    "status": "verified",
    "ttl": 0,
    "verified": "2025-09-26 13:18:19.838 +0000 UTC",
    "records_count": 0,
    "is_secondary_dns": true,
    "txt_verification": {
      "name": "string",
      "token": "string"
    }
  }
}
"""

RESPONSE_RECORDS_ALL = """
{
  "records": [
    {
      "type": "A",
      "id": "string",
      "created": "2025-09-26 13:18:19.838 +0000 UTC",
      "modified": "2025-09-26 13:18:19.838 +0000 UTC",
      "zone_id": "string",
      "name": "string",
      "value": "string",
      "ttl": 0
    }
  ]
}
"""

RESPONSE_RECORDS_SINGLE = """
{
  "record": {
    "type": "A",
    "id": "string",
    "created": "2025-09-26 13:18:19.838 +0000 UTC",
    "modified": "2025-09-26 13:18:19.838 +0000 UTC",
    "zone_id": "string",
    "name": "string",
    "value": "string",
    "ttl": 0
  }
}
"""


@pytest.mark.parametrize("body", [RESPONSE_ZONES_GET_ALL])
def test_decode_get_all(body: str) -> None:
    """Test decode of a get all request."""
    decoded = decode_object(body, type=DnsZoneListResponse)
    assert decoded is not None


@pytest.mark.parametrize("body", [RESPONSE_ZONE_CREATE])
def test_decode_create_zone(body: str) -> None:
    """Test decode of a create object."""
    decoded = decode_object(body, type=DnsZoneGetResponse)
    assert decoded is not None


@pytest.mark.parametrize("body", [RESPONSE_RECORDS_ALL])
def test_decode_records_all(body: str) -> None:
    """Test decoding of all records responses."""
    decoded = decode_object(body, type=DnsRecordListResponse)
    assert decoded is not None



@pytest.mark.parametrize("body", [RESPONSE_RECORDS_SINGLE])
def test_decode_records_single(body: str) -> None:
    """Decode single record response."""
    decoded = decode_object(body, type=DnsRecordItemResponse)
    assert decoded is not None
