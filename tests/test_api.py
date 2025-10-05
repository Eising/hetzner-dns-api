"""Test the API."""

import httpx
import math
import msgspec
import pytest
import re
from faker import Faker
from loguru import logger
from pytest_httpserver import HTTPServer

from werkzeug import Request
from werkzeug import Response

from hetzner_dns_api.decoding import enc_hook

from hetzner_dns_api.records import DnsRecord
from hetzner_dns_api.types import DnsBulkRecordCreateResponse, DnsRecordResponse, DnsZoneResponse
from hetzner_dns_api.zone import DnsZone
from .factories import (
    DnsBulkRecordCreateResponseFactory,
    DnsBulkRecordUpdateResponseFactory,
    DnsRecordItemResponseFactory,
    DnsRecordListResponseFactory,
    DnsRecordResponseFactory,
    DnsZoneGetResponseFactory,
    DnsZoneListResponseFactory,
    DnsZoneResponseFactory,
    PageMetaFactory,
    PageMetaResponseFactory,
)

DEFAULT_PER_PAGE = 100  # hetzner returns 100 objects per page


logger.enable("hetzner_dns_api")

class TestDnsRecord:
    """Test DNS records."""

    @pytest.fixture(autouse=True)
    def generate_responses(self, httpserver: HTTPServer) -> None:
        """Generate get response."""
        get_data = DnsRecordItemResponseFactory.create()
        get_data_obj = msgspec.to_builtins(get_data, enc_hook=enc_hook)
        list_data_content = DnsRecordResponseFactory.build_batch(10)
        list_data = DnsRecordListResponseFactory.create(records=list_data_content)
        list_data_obj = msgspec.to_builtins(list_data, enc_hook=enc_hook)
        httpserver.expect_request("/records", method="GET").respond_with_json(
            list_data_obj
        )
        httpserver.expect_request(
            re.compile(r"^/records/[^bulk][^/]+"), method="GET"
        ).respond_with_json(get_data_obj)
        httpserver.expect_request(
            re.compile(r"^/records/[^bulk][^/]+"), method="PUT"
        ).respond_with_json(get_data_obj)
        httpserver.expect_request("/records", method="POST").respond_with_json(
            get_data_obj
        )
        ok_response = Response(None, status=200)
        httpserver.expect_request(
            re.compile(r"^/records/[^bulk][^/]+"), method="DELETE"
        ).respond_with_response(ok_response)

        failed_updates = DnsRecordResponseFactory.build_batch(2)
        update_records = DnsRecordResponseFactory.build_batch(8)

        bulk_update_response = DnsBulkRecordUpdateResponseFactory.build(
            records=update_records, failed_records=failed_updates
        )
        bulk_update_response_obj = msgspec.to_builtins(
            bulk_update_response, enc_hook=enc_hook
        )

        create_records = DnsRecordResponseFactory.build_batch(10)
        invalid_creates = create_records[0:2]
        valid_creates = create_records[2:]
        bulk_create_response = DnsBulkRecordCreateResponseFactory.build(
            records=create_records,
            invalid_records=invalid_creates,
            valid_records=valid_creates,
        )

        bulk_create_response_obj = msgspec.to_builtins(
            bulk_create_response, enc_hook=enc_hook
        )
        httpserver.expect_request("/records/bulk", method="POST").respond_with_json(
            bulk_create_response_obj
        )
        httpserver.expect_request("/records/bulk", method="PUT").respond_with_json(
            bulk_update_response_obj
        )

    @pytest.fixture(name="dns_api")
    def api_fixture(self, httpserver: HTTPServer):
        """Create API instance."""
        base_url = f"http://{httpserver.host}:{httpserver.port}"
        client = httpx.Client(base_url=base_url)

        api = DnsRecord(client)
        yield api

    def test_record_list(self, dns_api: DnsRecord) -> None:
        """Test record list."""
        records = [record for record in dns_api.all("foo")]
        assert len(records) != 0

    def test_record_get(self, dns_api: DnsRecord, faker: Faker) -> None:
        """Test record get."""
        record = dns_api.get(faker.word())
        assert record is not None
        assert isinstance(record, DnsRecordResponse)

    def test_create(self, dns_api: DnsRecord, faker: Faker) -> None:
        """Test creation."""
        zone_id = faker.pystr(32, max_chars=32)
        name = faker.word()
        record_type = "A"
        value = faker.ipv4_public()
        ttl = faker.pyint(min_value=100, max_value=7200)
        response = dns_api.create(zone_id, name, record_type, value, ttl)
        assert response is not None
        assert isinstance(response, DnsRecordResponse)

    def test_update(self, dns_api: DnsRecord, faker: Faker) -> None:
        """Test update."""
        zone_id = faker.pystr(32, max_chars=32)
        record_id = faker.pystr(32, max_chars=32)
        name = faker.word()
        record_type = "A"
        value = faker.ipv4_public()
        ttl = faker.pyint(min_value=100, max_value=7200)
        response = dns_api.update(record_id, zone_id, name, record_type, value, ttl)
        assert response is not None
        assert isinstance(response, DnsRecordResponse)

    def test_delete(self, dns_api: DnsRecord, faker: Faker) -> None:
        """Test delete."""
        dns_api.delete(faker.word())

    def test_bulk_create(self, dns_api: DnsRecord, faker: Faker) -> None:
        """Test bulk create."""
        num_creations = 10
        zone_id = faker.pystr(32, max_chars=32)
        with dns_api.bulk_create() as bulk:
            for _ in range(num_creations):
                bulk.add(zone_id, faker.word(), "A", faker.ipv4_public())

            response = bulk.submit()

        assert response is not None
        assert isinstance(response, DnsBulkRecordCreateResponse)


@pytest.mark.parametrize("total_mock_records", [0, 10, 200])
class TestZones:
    """Test zone API methods."""

    @pytest.fixture(autouse=True)
    def generate_responses(self, httpserver: HTTPServer, total_mock_records: int, faker: Faker) -> None:
        """Generate responses.

        We only have one method here, so we can be a little bit more thorough in
        our implementation of the mock.
        """

        def all_handler(request: Request) -> Response:
            """Handle list responses."""
            total_entries = total_mock_records
            last_page = math.ceil(total_mock_records / DEFAULT_PER_PAGE)
            batch_count = min((DEFAULT_PER_PAGE, total_mock_records))
            page = 1
            if q_page := request.args.get("page"):
                page = int(q_page)

            entries = []
            if name := request.args.get("name"):
                entries = [DnsZoneResponseFactory(name=name)]
                last_page = 1
                total_entries = 1
            elif search_name := request.args.get("search_name"):
                for n in range(3):
                    newname = f"{search_name}-{n}.example"
                    entries.append(DnsZoneResponseFactory(name=newname))
                last_page = 1
                total_entries = 3


            page_meta = PageMetaFactory(page=page, per_page=DEFAULT_PER_PAGE, last_page=last_page, total_entries=total_entries)
            pagination = PageMetaResponseFactory(pagination=page_meta)
            if not entries:
                # This can be made more accurate for scenarios with odd numbers > per-page
                entries = DnsZoneResponseFactory.build_batch(batch_count)
            response_data = DnsZoneListResponseFactory(meta=pagination, zones=entries)
            encoded = msgspec.json.encode(response_data, enc_hook=enc_hook)
            return Response(encoded, content_type="application/json")

        def create_handler(request: Request) -> Response:
            """Handle create requests."""
            data = request.json
            assert isinstance(data, dict)
            name = data["name"]
            ttl: int | None = None
            if request_ttl := data.get("ttl"):
                ttl = int(request_ttl)
            zone_data = DnsZoneResponseFactory(name=str(name), ttl=ttl)
            response_data = DnsZoneGetResponseFactory(zone=zone_data)
            encoded = msgspec.json.encode(response_data, enc_hook=enc_hook)
            return Response(encoded, content_type="application/json")

        def get_handler(request: Request) -> Response:
            """Handle get one requests."""
            zone_id = request.path.split("/")[-1]
            name = faker.domain_name()
            zone_data = DnsZoneResponseFactory(name=name, id=zone_id)
            response_data = DnsZoneGetResponseFactory(zone=zone_data)
            encoded = msgspec.json.encode(response_data, enc_hook=enc_hook)
            return Response(encoded, content_type="application/json")


        httpserver.expect_request("/zones", method="GET").respond_with_handler(all_handler)
        httpserver.expect_request("/zones", method="POST").respond_with_handler(create_handler)
        httpserver.expect_request(re.compile(r"/zones/.*"), method="GET").respond_with_handler(get_handler)


    @pytest.fixture(name="dns_api")
    def api_fixture(self, httpserver: HTTPServer):
        """Create API instance."""
        base_url = f"http://{httpserver.host}:{httpserver.port}"
        client = httpx.Client(base_url=base_url)

        api = DnsZone(client)
        yield api

    def test_zone_list(self, dns_api: DnsZone, total_mock_records: int) -> None:
        """Test zone.all() method."""
        zones = [zone for zone in dns_api.all()]
        assert len(zones) == total_mock_records

    def test_zone_list_name(self, dns_api: DnsZone, faker: Faker) -> None:
        """List with a name query."""
        name = faker.domain_name()
        zones = [zone for zone in dns_api.all(name=name)]
        assert len(zones) == 1

    def test_zone_get_id(self, dns_api: DnsZone, faker: Faker) -> None:
        """Get get ID."""
        name = faker.domain_name()
        response = dns_api.get_id(name)
        assert response is not None


    def test_zone_list_searchname(self, dns_api: DnsZone, faker: Faker) -> None:
        """List with search name query."""
        name = faker.domain_word()
        zones = [zone for zone in dns_api.all(name=name, search=True)]
        assert len(zones) == 3

    def test_create(self, dns_api: DnsZone, faker: Faker) -> None:
        """Test creation."""
        name = faker.domain_name()
        response = dns_api.create(name=name, ttl=7200)
        assert isinstance(response, DnsZoneResponse)
        assert response.name == name

    def test_get_one(self, dns_api: DnsZone, faker: Faker) -> None:
        """Test get one zone."""
        zone_id = faker.pystr(min_chars=32, max_chars=32)
        response = dns_api.get(zone_id)
        assert isinstance(response, DnsZoneResponse)
