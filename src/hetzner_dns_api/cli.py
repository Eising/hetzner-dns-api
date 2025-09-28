"""CLI."""

import msgspec
from typing import cast
import click

from tabulate import tabulate
from hetzner_dns_api.types import DnsRecordResponse, DnsZoneResponse, RecordTypeCreatable
from hetzner_dns_api.decoding import enc_hook
from .api import HetznerDNS


def print_zone(zone: DnsZoneResponse) -> None:
    """Print a zone for CLI."""
    verified = "Verified"
    # header = f"{zone.id:<45}{click.style(zone.name, bold=True):<25}"
    # header = f"  {click.style(zone.name, bold=True)} ID {zone.id}"
    zone_name = zone.name
    if not zone.verified:
        verified = "Not Verified"

    click.echo(f"{zone.id:<25}{zone_name:<25}{verified:<10}")


def print_record(record: DnsRecordResponse):
    """Print a record."""
    # click.echo(f"{click.style(record.id, bold=True)}:")

    click.echo(
        f"Record ID: {record.id:<40}{record.name}\t{record.type !s}\t{record.value}\t{record.ttl or ''}"
    )


@click.group()
@click.option("--api-key", envvar="HETZNER_API_KEY")
@click.pass_context
def cli(ctx: click.Context, api_key: str) -> None:
    """Click context."""
    ctx.obj = HetznerDNS(api_key)


@cli.group("zone")
def cli_zone():
    pass


@cli_zone.command("list")
@click.pass_context
def cli_zone_list(ctx: click.Context) -> None:
    """List DNS zones."""
    api = cast(HetznerDNS, ctx.obj)

    click.echo(click.style("All Zones", bold=True))
    click.echo(f"{'Zone ID':<25}{'Name':<25}{'Verified':<10}")
    click.echo(f"{'-' * 60}")
    for zone in api.zones.all():
        print_zone(zone)


@cli.group("record")
def cli_record():
    pass


@cli_record.command("list")
@click.argument("zone-id")
@click.pass_context
def cli_record_list(ctx: click.Context, zone_id: str) -> None:
    """List records in a zone."""
    api = cast(HetznerDNS, ctx.obj)

    records = [
        msgspec.to_builtins(record, enc_hook=enc_hook)
        for record in api.records.all(zone_id)
    ]

    print(tabulate(records, headers="keys"))

@cli_record.command("create")
@click.argument("zone-id")
@click.argument("name")
@click.argument("type", type=click.Choice(RecordTypeCreatable, case_sensitive=False))
@click.argument("value")
@click.option("--ttl", type=click.INT)
@click.pass_context
def cli_record_add(ctx: click.Context, zone_id: str, name: str, type: RecordTypeCreatable, value: str, ttl: int | None) -> None:
    """Create a record in the given zone."""
    api = cast(HetznerDNS, ctx.obj)
    new_record = api.records.create(zone_id, name, type, value, ttl)
    click.echo(f"Record ID {new_record.id} created")
