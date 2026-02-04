"""bling tap class."""

from __future__ import annotations

import sys

import requests
from singer_sdk import Tap
from singer_sdk import typing as th
from singer_sdk.pagination import BaseAPIPaginator, TPageToken  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_bling.streams import InventoryStream, ProductsStream, blingStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override



class Tapbling(Tap):
    """Singer tap for bling."""

    name = "tap-bling"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            title="Client ID",
            description="Unique client ID provided by Bling"
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
            title="Client Secret",
            description="Unique client secret provided by Bling"
        ),
        th.Property(
            "bling_refresh_token",
            th.StringType,
            required=True,
            title="Bling Refresh Token",
            description="Unique refresh token provided by Bling used to get the current Barrer auth token"
        ),
        th.Property(
            "api_url",
            th.StringType(nullable=False),
            title="API URL",
            default="https://api.bling.com.br/Api/v3",
            description="The url for the API service",
        ),
        th.Property(
            "user_agent",
            th.StringType(nullable=True),
            description=(
                "A custom User-Agent header to send with each request. Default is "
                "'<tap_name>/<tap_version>'"
            ),
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[blingStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            InventoryStream(self),
            ProductsStream(self)
        ]


if __name__ == "__main__":
    Tapbling.cli()
