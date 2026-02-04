"""REST client handling, including blingStream base class."""

from __future__ import annotations

import decimal
import base64
import sys
from functools import cached_property
from typing import TYPE_CHECKING, Any, ClassVar

from singer_sdk import SchemaDirectory, StreamSchema
from singer_sdk.helpers import types
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator, TPageToken  # noqa: TC002
from singer_sdk.streams import RESTStream

from tap_bling import schemas
from tap_bling.auth import blingAuthenticator

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Iterable

    import requests
    from singer_sdk.helpers.types import Auth, Context


# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = SchemaDirectory(schemas)


class BlingPaginator(BaseAPIPaginator):

    def get_next(self, response: requests.Response) -> TPageToken | None:

        data = response.json().get("data", [])

        if not data:
            return None


        return self.current_value + 1

class blingStream(RESTStream):
    """bling inventory stream class."""

    # Update this value if necessary or override `parse_response`.
    records_jsonpath = "$[*]"

    # Update this value if necessary or override `get_new_paginator`.
    next_page_token_jsonpath = "$.next_page"  # noqa: S105


    last_id = None



    schema: ClassVar[StreamSchema] = StreamSchema(SCHEMAS_DIR)

    @override
    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return "https://api.bling.com.br/Api/v3"

    @override
    @cached_property
    def authenticator(self) -> Auth:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        client_id = self.config.get("client_id")

        client_secret = self.config.get("client_secret")

        raw_auth = f"{client_id}:{client_secret}"

        auth64 = base64.b64encode(raw_auth.encode("utf-8")).decode("utf-8")
        oauth_headers = {
            "Accept": "1.0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth64}"
        }


        return blingAuthenticator(
            auth_endpoint="https://api.bling.com.br/Api/v3/oauth/token",
            bling_refresh_token= self.config.get("bling_refresh_token"),
            client_id = client_id,
            client_secret = client_secret,
            oauth_headers = oauth_headers,

        )

    @property
    @override
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        return {}

    @override
    def get_new_paginator(self) -> BlingPaginator | None:
        """Create a new pagination helper instance.

        If the source API can make use of the `next_page_token_jsonpath`
        attribute, or it contains a `X-Next-Page` header in the response
        then you can remove this method.

        If you need custom pagination that uses page numbers, "next" links, or
        other approaches, please read the guide: https://sdk.meltano.com/en/v0.25.0/guides/pagination-classes.html.

        Returns:
            A pagination helper instance, or ``None`` to indicate pagination
            is not supported.
        """
        return BlingPaginator(start_value=1)

    # @override
    # def get_url_params(
    #     self,
    #     context: Context | None,
    #     next_page_token: Any | None,
    # ) -> dict[str, Any]:
    #     """Return a dictionary of values to be used in URL parameterization.
    #
    #     Args:
    #         context: The stream context.
    #         next_page_token: The next page index or value.
    #
    #     Returns:
    #         A dictionary of URL query parameters.
    #     """
    #     params: dict = {
    #         "limite": 100,
    #         "pagina": next_page_token or 1,
    #     }
    #
    #     if context and "product_id" in context:
    #         params["idsProdutos[]"] = self.config.get("products_ids")
    #     return params


    @override
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        # TODO: Parse response body and return a set of records.
        yield from extract_jsonpath(
            self.records_jsonpath,
            input=response.json(parse_float=decimal.Decimal),
        )

    @override
    def post_process(self, row, context=None):
        """Deduplicate rows by id or updated_at."""
        if not self.replication_key:
            return row

        row_id = row.get("id")
        row_updated_at = row.get(self.replication_key)

        if not row_id or not row_updated_at:
            return row

        if (
            row_id == self.last_id
            or row_updated_at == self.get_starting_replication_key_value(context)
        ):
            return None

        self.last_id = row_id
        return row