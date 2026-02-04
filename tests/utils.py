from tap_bling.tap import Tapbling

basic_mock_config = {'client_id': "1234", "client_secret": "5678", "bling_refresh_token": "54321"}

inventory_return_data = {
  "data": [
    {
      "produto": {

        "id": 12345678,
        "codigo": "12345678"
      },
      "saldoFisicoTotal": 1500.75,
      "saldoVirtualTotal": 1500.75,
      "depositos": [
        {
          "id": 12345678,
          "saldoFisico": 1250.75,
          "saldoVirtual": 1250.75
        }
      ]
    }
  ]
}