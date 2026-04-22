#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
import time
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

import porkbun_dns


SITE_VERIFICATION_BASE = "https://www.googleapis.com/siteVerification/v1"
SEARCH_CONSOLE_BASE = "https://www.googleapis.com/webmasters/v3"


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def access_token() -> str:
    for command in (
        ["gcloud", "auth", "print-access-token"],
        ["gcloud", "auth", "application-default", "print-access-token"],
    ):
        try:
            token = run(command)
            if token:
                return token
        except subprocess.CalledProcessError:
            continue
    raise SystemExit("Failed to obtain a Google access token from gcloud.")


def google_request(method: str, url: str, token: str, body: dict | None = None) -> tuple[int, str]:
    data = None
    headers = {"Authorization": f"Bearer {token}"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers, method=method)

    try:
        with urlopen(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8")
    except HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Google API request failed: {error.code} {details}") from error


def get_verification_token(domain: str, token: str) -> str:
    status, raw = google_request(
        "POST",
        f"{SITE_VERIFICATION_BASE}/token",
        token,
        {
            "verificationMethod": "DNS_TXT",
            "site": {"identifier": domain, "type": "INET_DOMAIN"},
        },
    )
    if status != 200:
        raise SystemExit(f"Unexpected getToken status: {status}")
    payload = json.loads(raw)
    return payload["token"]


def verify_domain(domain: str, token: str) -> dict:
    status, raw = google_request(
        "POST",
        f"{SITE_VERIFICATION_BASE}/webResource?verificationMethod=DNS_TXT",
        token,
        {"site": {"identifier": domain, "type": "INET_DOMAIN"}},
    )
    if status not in (200, 201):
        raise SystemExit(f"Unexpected verify status: {status}")
    return json.loads(raw)


def add_site_property(site_url: str, token: str) -> None:
    encoded = quote(site_url, safe="")
    status, _ = google_request("PUT", f"{SEARCH_CONSOLE_BASE}/sites/{encoded}", token)
    if status not in (200, 204):
        raise SystemExit(f"Unexpected Search Console site add status: {status}")


def submit_sitemap(site_url: str, sitemap_url: str, token: str) -> None:
    site = quote(site_url, safe="")
    sitemap = quote(sitemap_url, safe="")
    status, _ = google_request("PUT", f"{SEARCH_CONSOLE_BASE}/sites/{site}/sitemaps/{sitemap}", token)
    if status not in (200, 204):
        raise SystemExit(f"Unexpected sitemap submit status: {status}")


def wait_for_txt(domain: str, expected: str, timeout_seconds: int) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            output = run(["dig", "@8.8.8.8", "+short", "TXT", domain])
        except subprocess.CalledProcessError:
            output = ""

        if expected in output:
            return
        time.sleep(10)

    raise SystemExit(f"Timed out waiting for TXT record propagation on {domain}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a Porkbun-managed domain in Google Search Console.")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--sitemap-url", required=True)
    parser.add_argument("--wait-seconds", type=int, default=300)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    token = access_token()
    verification_token = get_verification_token(args.domain, token)
    porkbun_dns.ensure_txt_record(args.domain, "", verification_token, "600")
    wait_for_txt(args.domain, verification_token, args.wait_seconds)

    verify_domain(args.domain, token)
    site_url = f"sc-domain:{args.domain}"
    add_site_property(site_url, token)
    submit_sitemap(site_url, args.sitemap_url, token)

    print(f"GSC_SITE_URL={site_url}")
    print("GSC_OWNER_CONFIRMED=true")
    print("GSC_SITEMAP_SUBMITTED=true")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
