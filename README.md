# Introduction

This library provides an API as well as a CLI tool to manage DNS Zones and
Records hosted at Hetzner.

This library includes both a library and a small CLI application.

I have created this module as I couldn't find an existing one, and I needed one
for my ansible playbooks.

## Installation

The library is available on PyPi, and can be installed with `pip install hetzner-dns-api`

## CLI usage

<pre>
$ hetzner-dns --help
Usage: hetzner-dns [OPTIONS] COMMAND [ARGS]...

  Hetzner DNS API CLI client.

  Manage your hetzner DNS zones and entries.

  You must specify the API key either with --api-key or using the environment
  variable HETZNER_API_KEY.

Options:
  --api-key TEXT
  --help          Show this message and exit.

Commands:
  record
  zone
</pre>

### Zones
List or export zones.

Zone import is not implemented yet.

<pre>
$ hetzner-dns zone list --help

Usage: hetzner-dns zone list [OPTIONS]

  List DNS zones.

  You may narrow the zones returned with the options.

Options:
  --name TEXT
  --search
  --plain      Plain table without fancy text formatting
  --help       Show this message and exit.

</pre>

The `export` subcommand takes either a zone-id or the domain name.

<pre>
$ hetzner-api zone export --help
Usage: hetzner-dns zone export [OPTIONS] ZONE_ID_OR_NAME OUTPUT

  Export a zone.

Options:
  --help  Show this message and exit.
</pre>

Output can be a filename or `-` for stdout.

### Records
List, create, modify, or delete records

``` text
Usage: hetzner-dns record [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  create  Create a record in the given zone.
  delete  Delete a record.
  list    List records in a zone.
  update  Update a record.
```

#### Create

<pre>
Usage: hetzner-dns record create [OPTIONS] ZONE_ID_OR_NAME NAME {A|AAAA|NS|MX|
                                 CNAME|RP|TXT|SOA|HINFO|SRV|DANE|TLSA|DS|CAA}
                                 VALUE

  Create a record in the given zone.

Options:
  --ttl INTEGER
  --help         Show this message and exit.


</pre>
Example:

`hetzner-dns record create example.com www A 192.0.2.1`

If TTL is not specified, it will default to the default value for the Zone.

#### List

<pre>
Usage: hetzner-dns record list [OPTIONS] ZONE_ID_OR_NAME

  List records in a zone.

Options:
  --plain  Plain table without fancy text formatting
  --help   Show this message and exit.
</pre>

This will return a table view of all your records in a given zone. The zone may
be given as either the ID or the domain itself.

#### Update

<pre>
Usage: hetzner-dns record update [OPTIONS] RECORD_ID

  Update a record.

Options:
  --name TEXT
  --type [A|AAAA|NS|MX|CNAME|RP|TXT|SOA|HINFO|SRV|DANE|TLSA|DS|CAA]
  --value TEXT
  --ttl INTEGER
  --help                          Show this message and exit.
</pre>

You may specify any number of fields to update by providing the corresponding
option, however at least one option must be specified.

The record ID can be retrieved with the `list` command.

Example:

`hetzner-dns record update example.com MYRECORDID --ttl 600`

#### Delete

<pre>
Usage: hetzner-dns record delete [OPTIONS] RECORD_ID

  Delete a record.

Options:
  --help  Show this message and exit.
</pre>

## Usage as a python library

For an example of how to use the API, check out the CLI module `hetzner_dns_api.cli`.

### Initialize the API


``` python
from hetzner_dns_api import HetznerDNS

api = HetznerDNS("my-api-key")

```

### Zones

The `HetznerDNS.zones.list` method returns an iterator that will iterate through
all zones. This automatically takes in to account any paging done by the API
server.

The iterator yields a `hetzner_dns_api.types.DnsZoneResponse` object. This object is a `msgspec.Struct` object, containing all the properties provided by Hetzner's API.

``` python

from hetzner_dns_api import HetznerDNS

api = HetznerDNS("my-api-key")

for zone in api.zones.all():
    # do something with the zone object

```

See `hetzner_dns_api.DnsZone` for more info on what you can do with Zones.

### Records

Records is implemented in the `hetzner_dns_api.types.DnsRecord` class, which is
conveniently available as `.records` in the `HetznerDNS` class instance.

``` python
from hetzner_dns_api import HetznerDNS

api = HetznerDNS("my-api-key")

# Get the zone_id of a domain
zone_id = api.zones.get_id("example.com")

# Create www.example.com A-record with 192.0.2.1 as value, and the zone default ttl
new_record = api.records.create(zone_id, name="www", record_type="A", value="192.0.2.1")

# Print the new record ID
print(new_record.id)

# Update the TTL of the record (or any other field)
updated_record = api.records.update(new_record.id, zone_id=zone_id, ttl=600)

# delete the newly created record
api.records.delete(new_record.id)

```

There's also methods for bulk creation, implemented as context managers:

``` python

api = HetznerDNS("my-api-key")

with api.records.bulk_create() as bulk:
    for num in range(200):
        bulk.add(zone_id="my-zone-id", name=f"host{num}", record_type="AAAA", value=f"2001:db8:f00::{num}")
    changeset = bulk.submit()
    
# Get all my record-ids
records = [record.id for record in api.records.all(zone_id="my-zone-id")]

with api.records.bulk_update() as bulk:
    for record_id in records:
        bulk.add(record_id, "my-zone-id", ttl=600)
    changeset = bulk.submit()

```

For bulk-creation, the `.submit()` function returns a
`hetzner_dns_api.types.DnsBulkRecordCreateResponse` while the update one, returns a
`hetzner_dns_api.types.DnsBulkRecordUpdateResponse`.








