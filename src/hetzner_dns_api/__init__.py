"""Python library and CLI app to manage DNS hosted by Hetzner, the German
hosting provider.

.. include:: ../../README.md

# Python API documentation

The public python API is available through the `HetznerDNS` class which takes
care of all instantiation of all other classes and sub-APIs.

You should never need to initialize any of the other classes yourself.

"""

from .api import HetznerDNS
from .records import DnsBulkCreateRecord, DnsBulkUpdateRecord, DnsRecord
from . import types
from .zone import DnsZone

__all__ = [
    "HetznerDNS",
    "DnsZone",
    "DnsRecord",
    "DnsBulkCreateRecord",
    "DnsBulkUpdateRecord",
    "types",
]
