"""
HTTP transport layer — the only module that talks to the network.

Follows the Interface Segregation Principle: exposes only what callers need
(execute / set_header / set_cookie).
"""
from __future__ import annotations

from typing import Dict, Optional

import requests
import urllib3

from .config import DEFAULT_TIMEOUT, USER_AGENT
from .exceptions import NetworkError

# Suppress InsecureRequestWarning when verify_ssl=False (common in CTF environments)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NetworkClient:
    """
    Abstracts HTTP GET/POST communication with a remote web shell endpoint.

    Supports:
      - GET and POST payloads
      - Custom HTTP request headers
      - Custom cookies (e.g. session auth tokens)
      - SSL verification toggle (handy for self-signed CTF certs)
    """

    def __init__(
        self,
        url: str,
        param: str,
        method: str = "GET",
        timeout: int = DEFAULT_TIMEOUT,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        verify_ssl: bool = False,
    ) -> None:
        self.url = url
        self.param = param
        self.method = method.upper()
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        self._http = requests.Session()
        self._http.headers.update({"User-Agent": USER_AGENT})
        if headers:
            self._http.headers.update(headers)
        if cookies:
            self._http.cookies.update(cookies)

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def execute(self, command: str) -> str:
        """
        Send *command* to the web shell and return the raw response body.
        Raises NetworkError on any transport / HTTP failure.
        """
        try:
            if self.method == "GET":
                resp = self._http.get(
                    self.url,
                    params={self.param: command},
                    timeout=self.timeout,
                    verify=self.verify_ssl,
                )
            elif self.method == "POST":
                resp = self._http.post(
                    self.url,
                    data={self.param: command},
                    timeout=self.timeout,
                    verify=self.verify_ssl,
                )
            else:
                raise NetworkError(f"Unsupported HTTP method: {self.method}")

            resp.raise_for_status()
            return resp.text.strip()

        except requests.exceptions.Timeout:
            raise NetworkError("Request timed out — is the target reachable?")
        except requests.exceptions.SSLError as exc:
            raise NetworkError(f"SSL error (try adding verify=False): {exc}")
        except requests.exceptions.ConnectionError as exc:
            raise NetworkError(f"Connection refused / unreachable: {exc}")
        except requests.exceptions.HTTPError as exc:
            raise NetworkError(
                f"HTTP {exc.response.status_code} from target — check the URL and param name."
            )
        except requests.exceptions.RequestException as exc:
            raise NetworkError(str(exc))

    def set_header(self, key: str, value: str) -> None:
        """Persist a custom request header for all future requests on this session."""
        self._http.headers[key] = value

    def set_cookie(self, key: str, value: str) -> None:
        """Persist a cookie for all future requests on this session."""
        self._http.cookies.set(key, value)

