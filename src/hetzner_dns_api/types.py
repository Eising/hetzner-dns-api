"""Types."""
import enum
from datetime import datetime
from typing import override
import msgspec


class HetznerTime(datetime):
    """
    Custom datetime instance.

    This class is identical to datetime.datetime, and exists only to facilitate
    encoding/decoding the custom time format that Hetzner uses.
    """


class VerifiedTime:
    """Hetzner uses a non-RFC compliant datetime object."""

    def __init__(self, verified: bool, timestamp: HetznerTime | None = None) -> None:
        """Init verified time object."""
        self.verified: bool = verified
        self.timestamp: HetznerTime | None = None

    @override
    def __repr__(self) -> str:
        """Generate string representation."""
        if self.verified and self.timestamp:
            return f"VerifiedTime({self.timestamp.isoformat()})"
        return "VerifiedTime(Unavailable)"


class PageMeta(msgspec.Struct):
    """Paging metadata."""

    page: int
    per_page: int
    last_page: int
    total_entries: int


class PageMetaResponse(msgspec.Struct):
    """Page meta response."""

    pagination: PageMeta


class QueryParams(msgspec.Struct):
    """Query parameters."""

    page: int = 1
    per_page: int = 100
    search_name: str | None = None



class ZoneStatus(str, enum.Enum):
    """Zone status."""

    VERIFIED = "verified"
    FAILED = "failed"
    PENDING = "pending"


class RecordType(enum.StrEnum):
    """Dns Record Type."""

    A = "A"
    AAAA = "AAAA"
    PTR = "PTR"
    NS = "NS"
    MX = "MX"
    CNAME = "CNAME"
    RP = "RP"
    TXT = "TXT"
    SOA = "SOA"
    HINFO = "HINFO"
    SRV = "SRV"
    DANE = "DANE"
    TLSA = "TLSA"
    DS = "DS"
    CAA = "CAA"


class RecordTypeCreatable(enum.StrEnum):
    """Creatable DNS record type."""

    A = "A"
    AAAA = "AAAA"
    NS = "NS"
    MX = "MX"
    CNAME = "CNAME"
    RP = "RP"
    TXT = "TXT"
    SOA = "SOA"
    HINFO = "HINFO"
    SRV = "SRV"
    DANE = "DANE"
    TLSA = "TLSA"
    DS = "DS"
    CAA = "CAA"


class DnsZoneTxtVerification(msgspec.Struct):
    """Dns zone TXT record to verify zone."""

    name: str
    token: str



class DnsZoneResponse(msgspec.Struct):
    """Dns Zone definition."""

    created: HetznerTime
    id: str
    is_secondary_dns: bool
    legacy_dns_host: str | None
    legacy_ns: list[str]
    modified: HetznerTime
    name: str
    ns: list[str]
    owner: str
    paused: bool
    records_count: int
    registrar: str
    status: ZoneStatus
    ttl: int
    txt_verification: DnsZoneTxtVerification | None
    verified: VerifiedTime


class DnsZoneGetResponse(msgspec.Struct):
    """Dns Zone Created Response."""

    zone: DnsZoneResponse


class DnsZoneListResponse(msgspec.Struct):
    """Dns Zone List Response."""

    meta: PageMetaResponse
    zones: list[DnsZoneResponse]


class DnsRecordResponse(msgspec.Struct):
    """Dns Record Response."""

    created: HetznerTime
    id: str
    modified: HetznerTime
    name: str
    type: RecordType
    value: str
    zone_id: str
    ttl: int | None = None


class DnsZoneValidationResponse(msgspec.Struct):
    """Dns Zone Validation Response."""

    parsed_records: int
    valid_records: list[DnsRecordResponse]


class DnsRecordListResponse(msgspec.Struct):
    """Dns record list response."""

    records: list[DnsRecordResponse]

class DnsRecordItemResponse(msgspec.Struct):
    """Dns Record Item Response."""

    record: DnsRecordResponse


class DnsRecordRequest(msgspec.Struct):
    """Dns Record create Request."""

    zone_id: str
    name: str
    type: RecordTypeCreatable
    value: str
    ttl: int | None = None


class DnsRecordBulkCreateRequest(msgspec.Struct):
    """Dns Record Bulk Create Request."""

    records: list[DnsRecordRequest] = msgspec.field(default_factory=list)


class DnsRecordUpdateRequest(msgspec.Struct):
    """Dns Record bulk update Request."""

    id: str
    zone_id: str
    name: str
    type: RecordTypeCreatable
    value: str
    ttl: int | None = None

class DnsRecordBulkUpdateRequest(msgspec.Struct):
    """Dns Record Bulk Update Request."""

    records: list[DnsRecordUpdateRequest] = msgspec.field(default_factory=list)



class DnsBulkRecordCreateResponse(msgspec.Struct):
    """Dns Record Bulk Create Response."""

    records: list[DnsRecordResponse]
    valid_records: list[DnsRecordRequest]
    invalid_records: list[DnsRecordRequest]


class DnsBulkRecordUpdateResponse(msgspec.Struct):
    """Dns Record Bulk Update Response."""

    records: list[DnsRecordResponse]
    failed_records: list[DnsRecordRequest]


__all__ = [
    "DnsBulkRecordCreateResponse",
    "DnsBulkRecordUpdateResponse",
    "DnsZoneValidationResponse",
    "DnsRecordRequest",
    "DnsRecordResponse",
    "DnsZoneResponse",
]
