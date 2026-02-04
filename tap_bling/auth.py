"""bling Authentication."""

from __future__ import annotations

import sys
import base64
import urllib.parse

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta


if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class blingAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for bling."""

    def __init__(
            self,
            bling_refresh_token: str,
            client_id: str,
            client_secret: str,
            oauth_headers: dict[str, str],
            *args,
            **kwargs,
    ):
        super().__init__(bling_refresh_token = bling_refresh_token, client_id=client_id, client_secret=client_secret, oauth_headers=oauth_headers, *args, **kwargs)

        self._bling_refresh_token = bling_refresh_token
        self._client_id = client_id
        self._client_secret = client_secret

        raw_auth = f"{self._client_id}:{self._client_secret}"
        auth64 = base64.b64encode(raw_auth.encode("utf-8")).decode("utf-8")
        self._oauth_headers = {
            "Accept": "1.0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth64}"
        }

    @property
    def oauth_request_body(self) -> dict:
        """Build up a list of OAuth2 parameters.

        Build up a list of OAuth2 parameters to use depending
        on what configuration items have been set and the type of OAuth
        flow set by the grant_type.
        """

        oauth_params = {}

        return oauth_params



    @property
    def oauth_request_payload(self) -> dict:
        """Get request body for the token endpoint.

        Bling Requirement: Only grant_type and refresh_token go in the body.
        """

        body = {
            "grant_type": "refresh_token",
            "refresh_token": self._bling_refresh_token,
        }

        return body
