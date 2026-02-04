# Singer tap for Bling!

This Bling! tap produces JSON-formatted data following the Singer spec.

[![Python](https://img.shields.io/static/v1?logo=python&label=python&message=3.10%20|%203.11%20|%203.12%20|%203.13%20|%203.14&color=blue)]()


`tap-bling` is a Singer tap for the [Bling! REST API](https://developer.bling.com.br/referencia) 
built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

<!--

Developer TODO: Update the below as needed to correctly describe the install procedure. For instance, if you do not have a PyPI repo, or if you want users to directly install from your git repo, you can modify this step as appropriate.

## Installation

Install from PyPI:

```bash
uv tool install tap-bling
```

Install from GitHub:

```bash
uv tool install git+https://github.com/ORG_NAME/tap-bling.git@main
```

-->

## Configuration file

How to get your refresh token: [Bling Docs](https://developer.bling.com.br/aplicativos).

*  `bling_refresh_token` String (required) - The refresh token to request Bling API access token.
*  `client_id` String (required) - Bling API client ID, required to authenticate and request Bling API access token.
*  `client_secret` String (required) - Bling API client secret, required to authenticate and request Bling API access token.
*  `auth_endpoint` String (required) - Bling API endpoint for requesting the access token.
*  `start_date` String (optional) - The earliest record date to sync.


## Supported Streams

### Default Streams
* [Products](https://api.bling.com.br/Api/v3/products)
* [Inventory](https://api.bling.com.br/Api/v3/products)

## Roadmap

- [ ] Add new default streams (Invoices, Orders, Sales-channels, Payables, Receivables)
- [ ] 


## Accepted Config Options

<!--
Developer TODO: Provide a list of config options accepted by the tap.

This section can be created by copy-pasting the CLI output from:

```
tap-bling --about --format=markdown
```
-->

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-bling --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

Source Authentication and Authorization
To extract data from Bling ERP (API v3), this tap requires OAuth2 credentials. Because Bling uses a short-lived Access Token flow, you must provide a Refresh Token which the tap will use to maintain a persistent connection.

#### 1.  Create a Bling App Integration 
   Log in to the Bling Developer Portal.

Navigate to Meus Aplicativos (My Apps).

Click Cadastrar Aplicativo.

Fill in the basic details:

Nome: Meltano Data Tap (or your internal project name).

Callback URL: http://localhost:8080 (This is required for the authorization step, even if running headless).

In the Scopes section, select the resources you intend to extract. To match the tap's capabilities, ensure you select "Read" (Leitura) permissions for entities such as:

* vendas (Sales/Orders)

* produtos (Products)

* contatos (Customers/Suppliers)

* estoques (Inventory)

* Save the application.

* Copy the Client ID and Client Secret.

#### 2. Generate the Initial Refresh Token

***Note**: Since this is a backend data pipeline, you must perform the initial "Handshake" manually to generate the first token.*

A. Get the Authorization Code Paste the following URL into your browser, replacing `YOUR_CLIENT_ID` with the ID from Step 1:


`https://www.bling.com.br/Api/v3/oauth/authorize?response_type=code&client_id=YOUR_CLIENT_ID&state=state_demo`

Click Authorize (Autorizar) on the Bling consent screen.

You will be redirected to your Callback URL (e.g., localhost).

Look at the URL in your browser address bar. It will look like this: `http://localhost:8080/?code=YOUR_AUTHORIZATION_CODE&state=state_demo`

Copy the `YOUR_AUTHORIZATION_CODE` value.

B. Exchange Code for Refresh Token Run the following curl command in your terminal (or use Postman). Replace the placeholders with your actual values:

```Bash
curl -X POST "https://www.bling.com.br/Api/v3/oauth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -u "YOUR_CLIENT_ID:YOUR_CLIENT_SECRET" \
     -d "grant_type=authorization_code" \
     -d "code=YOUR_AUTHORIZATION_CODE"
```
The response will contain your `refresh_token`.

## Usage

You can easily run `tap-bling` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-bling --version
tap-bling --help
tap-bling --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

Prerequisites:

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

```bash
uv sync
```

### Create and Run Tests

Create tests within the `tests` subfolder and
then run:

```bash
uv run pytest
```

You can also test the `tap-bling` CLI interface directly using `uv run`:

```bash
uv run tap-bling --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

<!--
Developer TODO:
Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any "TODO" items listed in
the file.
-->

Use Meltano to run an EL pipeline:

```bash
# Install meltano
uv tool install meltano

# Test invocation
meltano invoke tap-bling --version

# Run a test EL pipeline
meltano run tap-bling target-jsonl
```

---

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
