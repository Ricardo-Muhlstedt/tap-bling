import unittest
from unittest.mock import patch, MagicMock
from tap_bling.streams import InventoryStream


class TestInventoryBatching(unittest.TestCase):
    """
    Architectural Test: Verifies that InventoryStream correctly
    slices the 'Universe' of Product IDs into API-safe batches.
    """

    def setUp(self):

        self.tap = MagicMock()
        self.tap.config = {}


        self.stream = InventoryStream(tap=self.tap)

    def test_partitions_logic(self):
        """
        Scenario: 150 Products exist.
        Expected: 2 Partitions (Batch 1=100, Batch 2=50).
        """
        mock_products_stream = MagicMock()
        fake_records = [{"id": i} for i in range(1, 151)]
        mock_products_stream.get_records.return_value = fake_records

        self.tap.streams = {"products": mock_products_stream}

        partitions = self.stream.partitions

        self.assertIsNotNone(partitions)
        self.assertEqual(len(partitions), 2, "Should split 150 items into 2 batches")

        self.assertEqual(len(partitions[0]["product_ids"]), 100)
        self.assertEqual(len(partitions[1]["product_ids"]), 50)

    def test_request_parameters_format(self):
        """
        Scenario: A partition context is provided.
        Expected: The params dict contains 'idsProdutos[]' with the list.
        """

        mock_context = {"product_ids": [10, 20, 30]}

        params = self.stream.get_url_params(context=mock_context, next_page_token=None)

        self.assertIn("idsProdutos[]", params)
        self.assertEqual(
            params["idsProdutos[]"],
            [10, 20, 30],
            "Must pass the list exactly as required by Bling V3"
        )

        self.assertEqual(params.get("limite"), 100)