"""CLI."""

import sys
import enum
from typing import cast, TextIO

import msgspec
import click

from tabulate import tabulate
from hetzner_dns_api.base import HetznerApiError, HetznerApiNotFoundError
from hetzner_dns_api.types import (
    DnsRecordResponse,
    RecordType,
    RecordTypeCreatable,
)
from hetzner_dns_api.decoding import enc_hook
from .api import HetznerDNS


class OutputFormat(enum.StrEnum):
    """Output format."""

    TABLE = "table"
    SIMPLE_TABLE = "simple_table"
    JSON = "json"


def print_record(record: DnsRecordResponse):
    """Print a record."""
    # click.echo(f"{click.style(record.id, bold=True)}:")

    click.echo(
        f"Record ID: {record.id:<40}{record.name}\t{record.type !s}\t{record.value}\t{record.ttl or ''}"
    )


def lookup_zone_id(api: HetznerDNS, id_or_name: str) -> str | None:
    """Lookup a zone ID by either ID or domain name."""
    if "." in id_or_name:
        return api.zones.get_id(id_or_name)
    try:
        zone = api.zones.get(id_or_name)
        return zone.id
    except HetznerApiError:
        return None


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
@click.option("--name")
@click.option("--search", is_flag=True)
@click.option("--plain", help="Plain table without fancy text formatting", is_flag=True)
@click.pass_context
def cli_zone_list(
    ctx: click.Context, name: str | None, search: bool, plain: bool
) -> None:
    """List DNS zones."""
    api = cast(HetznerDNS, ctx.obj)
    table_format = "simple" if plain else "rounded_grid"

    entries = [zone for zone in api.zones.all(name=name, search=search)]
    if not entries:
        click.echo("No zones found.")
        sys.exit()

    # longest_line = max([len(line) for line in entries])
    headers = ["Zone ID", "Name", "Verified", "Created", "Last Modified"]
    rows = [
        [
            zone.id,
            zone.name,
            "Verified" if zone.verified else "Not Verified",
            zone.created,
            zone.modified,
        ]
        for zone in entries
    ]

    click.echo(tabulate(rows, headers=headers, tablefmt=table_format))


@cli_zone.command("export")
@click.argument("zone-id-or-name")
@click.argument("output", type=click.File(mode="w+"))
@click.pass_context
def cli_zone_export(ctx: click.Context, zone_id_or_name: str, output: TextIO) -> None:
    """Export a zone."""
    api = cast(HetznerDNS, ctx.obj)

    zone_id = lookup_zone_id(api, zone_id_or_name)
    if not zone_id:
        raise click.ClickException(f"No zone found with ID or name {zone_id_or_name}")

    exported = api.zones.export_zone(zone_id)
    result = output.write(exported)
    if not output.isatty():
        click.echo(f"Wrote {result} characters to {output.name}.")


@cli.group("record")
def cli_record():
    pass


@cli_record.command("list")
@click.argument("zone-id-or-name")
@click.option("--plain", help="Plain table without fancy text formatting", is_flag=True)
@click.pass_context
def cli_record_list(ctx: click.Context, zone_id_or_name: str, plain: bool) -> None:
    """List records in a zone."""
    table_format = "simple" if plain else "rounded_grid"
    api = cast(HetznerDNS, ctx.obj)

    zone_id = lookup_zone_id(api, zone_id_or_name)
    if not zone_id:
        raise click.ClickException(f"No zone found with ID or name {zone_id_or_name}")

    try:
        records = [
            msgspec.to_builtins(record, enc_hook=enc_hook)
            for record in api.records.all(zone_id)
        ]
    except HetznerApiNotFoundError as e:
        raise click.ClickException(f"Zone ID {zone_id} not found.") from e

    print(tabulate(records, headers="keys", tablefmt=table_format))


@cli_record.command("create")
@click.argument("zone-id-or-name")
@click.argument("name")
@click.argument("type", type=click.Choice(RecordTypeCreatable, case_sensitive=False))
@click.argument("value")
@click.option("--ttl", type=click.INT)
@click.pass_context
def cli_record_add(
    ctx: click.Context,
    zone_id_or_name: str,
    name: str,
    type: RecordTypeCreatable,
    value: str,
    ttl: int | None,
) -> None:
    """Create a record in the given zone."""
    api = cast(HetznerDNS, ctx.obj)
    zone_id = lookup_zone_id(api, zone_id_or_name)

    if not zone_id:
        raise click.ClickException(f"No zone found with ID or name {zone_id_or_name}")

    new_record = api.records.create(zone_id, name, type, value, ttl)
    click.echo(f"Record ID {new_record.id} created")


@cli_record.command("update")
@click.argument("record-id")
@click.option("--name")
@click.option("--type", type=click.Choice(RecordTypeCreatable, case_sensitive=False))
@click.option("--value")
@click.option("--ttl", type=click.INT)
@click.pass_context
def cli_record_update(
    ctx: click.Context,
    record_id: str,
    name: str | None,
    type: RecordTypeCreatable | None,
    value: str | None,
    ttl: int | None,
) -> None:
    """Update a record."""
    if not any(
        (
            name,
            type,
            value,
            ttl,
        )
    ):
        raise click.ClickException("Must specify at least one field to update.")

    api = cast(HetznerDNS, ctx.obj)
    record = api.records.get(record_id)
    new_type: RecordTypeCreatable | RecordType = type or record.type

    updated = api.records.update(
        record_id=record_id,
        zone_id=record.zone_id,
        name=name or record.name,
        record_type=new_type,
        value=value or record.value,
        ttl=ttl or record.ttl,
    )

    click.echo(f"Updated record {record_id} in zone {record.zone_id}")
    print_record(updated)


@cli_record.command("delete")
@click.argument("record-id")
@click.pass_context
def cli_record_delete(ctx: click.Context, record_id: str) -> None:
    """Delete a record."""
    api = cast(HetznerDNS, ctx.obj)
    record = api.records.get(record_id)
    click.echo(click.style("Delete record", bold=True))
    print_record(record)
    if click.confirm("Are you sure you want to delete the record?"):
        api.records.delete(record_id)
    else:
        click.echo("Aborted.")
