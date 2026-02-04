"""Stream type classes for tap-bling."""

from __future__ import annotations

import typing as t

from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.helpers import types

from typing import ClassVar, override, Any

from singer_sdk.helpers.types import Context
from singer_sdk.streams.rest import _TToken

from tap_bling.client import blingStream

from tap_bling import schemas

from singer_sdk import StreamSchema, SchemaDirectory

SCHEMAS_DIR = SchemaDirectory(schemas)

class ProductsStream(blingStream):
    """Bling product stream."""
    name = "products"
    path = "/products"
    records_jsonpath = "$.data[*]"
    primary_key = "id"
    replication_key = None

    schema: ClassVar[StreamSchema] = StreamSchema(SCHEMAS_DIR)

    def get_child_context(
        self,
        record: types.Record,
        context: types.Context | None,
    ) -> types.Context | None:
        return {
            "product_id": record["id"]
        }

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {
            "limite": 100,
            "pagina": next_page_token or 1,
        }

        return params

class InventoryStream(blingStream):
    name = "inventory"
    path = "/estoques/saldos"
    records_jsonpath = "$.data[*]"
    primary_keys = ["produto.id"]
    state_partitioning_keys = ["product_ids"]

    @property
    def partitions(self) -> list[dict] | None:
        """Divide product IDs into batches of 100."""
        products_stream = self._tap.streams.get("products")
        if not products_stream:
            return []


        all_ids = [record["id"] for record in products_stream.get_records(context=None)]

        if not all_ids:
            return []

        batch_size = 100
        return [
            {"product_ids": all_ids[i: i + batch_size]}
            for i in range(0, len(all_ids), batch_size)
        ]

    @override
    def get_url_params(
            self,
            context: Context | None,
            next_page_token: Any | None,
    ) -> dict[str, Any]:
        params = {
            "limite": 100,
            "pagina": next_page_token or 1,
        }
        if context and "product_ids" in context:
            params["idsProdutos[]"] = context["product_ids"]
        return params