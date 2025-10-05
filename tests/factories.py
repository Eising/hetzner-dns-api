"""Test data factories.

I'm counting on msgspec's ability to de-serialize, in order to produce realistic
JSON responses.

"""

from datetime import timezone
from typing import Any, override
import factory
from faker import Faker
from hetzner_dns_api.types import (
    DnsBulkRecordCreateResponse,
    DnsBulkRecordUpdateResponse,
    DnsRecordItemResponse,
    DnsRecordRequest,
    DnsRecordResponse,
    DnsRecordListResponse,
    DnsZoneGetResponse,
    DnsZoneListResponse,
    DnsZoneResponse,
    HetznerTime,
    PageMetaResponse,
    PageMeta,
    ZoneStatus,
)


faker = Faker()


def gen_timestamp(*_args: Any, **_kwargs: Any) -> HetznerTime:
    """Generate timestamp."""
    return HetznerTime.now(timezone.utc)


def gen_ns(*_args: Any, **_kwargs: Any) -> list[str]:
    """Generate ns entries."""
    base_domain = faker.domain_name()
    servers = []
    for n in range(1, 4):
        dns = f"ns{n}.{base_domain}"
        servers.append(dns)

    return servers


def create_records_list(*args: Any, **kwargs: Any) -> list[DnsRecordResponse]:
    """Create a list of records."""
    return DnsRecordResponseFactory.build_batch(10)


class PageMetaFactory(factory.Factory[PageMeta]):
    """Page Meta Factory."""

    class Meta:
        model = PageMeta

    page = 1
    per_page = 100
    last_page = 1
    total_entries = 10


class PageMetaResponseFactory(factory.Factory[PageMetaResponse]):
    """Page meta response factory."""

    class Meta:
        model = PageMetaResponse

    pagination = factory.SubFactory(PageMetaFactory)


class DnsRecordResponseFactory(factory.Factory[DnsRecordResponse]):
    """Dns Record Response Factory."""

    @override
    class Meta:
        model = DnsRecordResponse

    created = factory.lazy_attribute(gen_timestamp)
    id = factory.Faker("pystr", min_chars=32, max_chars=32)
    modified = factory.lazy_attribute(gen_timestamp)
    name = factory.Faker("word")
    type = factory.Iterator(["A", "AAAA", "CNAME", "MX", "TXT"])
    value = factory.Faker("ipv4_public")
    zone_id = factory.Faker("pystr", min_chars=32, max_chars=32)
    ttl = None


class DnsRecordRequestFactory(factory.Factory[DnsRecordRequest]):
    """Dns Record Request Factory."""

    @override
    class Meta:
        model = DnsRecordRequest

    zone_id = factory.Faker("pystr", min_chars=32, max_chars=32)
    name = factory.Faker("word")
    type = factory.Iterator(["A", "AAAA", "CNAME", "MX", "TXT"])
    value = factory.Faker("ipv4_public")
    zone_id = factory.Faker("pystr", min_chars=32, max_chars=32)
    ttl = None


class DnsRecordListResponseFactory(factory.Factory[DnsRecordListResponse]):
    """DNS Record List Response Factory."""

    @override
    class Meta:
        model = DnsRecordListResponse

    records = []


class DnsRecordItemResponseFactory(factory.Factory[DnsRecordItemResponse]):
    """DNS Record Item Response Factory."""

    @override
    class Meta:
        model = DnsRecordItemResponse

    record = factory.SubFactory(DnsRecordResponseFactory)


class DnsBulkRecordCreateResponseFactory(factory.Factory[DnsBulkRecordCreateResponse]):
    """Dns Bulk Record Create Response Factory."""

    @override
    class Meta:
        model = DnsBulkRecordCreateResponse

    records = []
    valid_records = []
    invalid_records = []


class DnsBulkRecordUpdateResponseFactory(factory.Factory[DnsBulkRecordUpdateResponse]):
    """Dns Bulk Record Create Response Factory."""

    @override
    class Meta:
        model = DnsBulkRecordUpdateResponse

    records = []
    failed_records = []


class DnsZoneResponseFactory(factory.Factory[DnsZoneResponse]):
    """Dns Zone Response Factory."""

    @override
    class Meta:
        model = DnsZoneResponse

    created = factory.lazy_attribute(gen_timestamp)
    id = factory.Faker("pystr", min_chars=32, max_chars=32)
    is_secondary_dns = False
    legacy_dns_host = None
    legacy_ns = []
    modified = factory.lazy_attribute(gen_timestamp)
    name = factory.Faker("domain_name")
    ns = factory.lazy_attribute(gen_ns)
    owner = ""
    paused = False
    records_count = 10
    registrar = ""
    status = ZoneStatus.VERIFIED
    ttl = 7200
    txt_verification = {"name": "", "token": ""}
    verified = ""


class DnsZoneListResponseFactory(factory.Factory[DnsZoneListResponse]):
    """Dns Zone List Response Factory."""

    @override
    class Meta:
        model = DnsZoneListResponse

    meta = factory.SubFactory(PageMetaResponseFactory)
    zones = []


class DnsZoneGetResponseFactory(factory.Factory[DnsZoneGetResponse]):
    """Dns Zone Get Response factory."""

    @override
    class Meta:
        model = DnsZoneGetResponse

    zone = factory.SubFactory(DnsZoneResponseFactory)
