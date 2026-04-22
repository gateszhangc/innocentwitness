#!/usr/bin/env python3

import argparse
import ssl
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def fetch(url: str) -> tuple[int, str]:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    context = ssl.create_default_context()

    try:
        with urlopen(request, timeout=20, context=context) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except HTTPError as error:
        return error.code, error.read().decode("utf-8", errors="replace")
    except URLError as error:
        raise SystemExit(f"Request failed for {url}: {error}") from error


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test the live innocentwitness site.")
    parser.add_argument("--base-url", default="https://innocentwitness.lol")
    return parser.parse_args()


def assert_contains(haystack: str, needle: str, label: str) -> None:
    if needle not in haystack:
        raise SystemExit(f"Expected {label} to contain {needle!r}")


def main() -> int:
    args = parse_args()
    base_url = args.base_url.rstrip("/")

    status, body = fetch(f"{base_url}/")
    if status != 200:
        raise SystemExit(f"Expected homepage status 200, got {status}")
    assert_contains(body, "無垢なる証人", "homepage")
    assert_contains(body, 'rel="canonical" href="https://innocentwitness.lol/"', "homepage canonical")
    if "Parked on the Bun!" in body:
        raise SystemExit("Homepage is still showing the Porkbun parked page.")
    if "googletagmanager.com" in body or "clarity.ms" in body:
        raise SystemExit("Unexpected analytics scripts were found in the homepage HTML.")

    robots_status, robots = fetch(f"{base_url}/robots.txt")
    if robots_status != 200:
        raise SystemExit(f"Expected robots.txt status 200, got {robots_status}")
    assert_contains(robots, "Sitemap: https://innocentwitness.lol/sitemap.xml", "robots.txt")

    sitemap_status, sitemap = fetch(f"{base_url}/sitemap.xml")
    if sitemap_status != 200:
        raise SystemExit(f"Expected sitemap.xml status 200, got {sitemap_status}")
    assert_contains(sitemap, "<loc>https://innocentwitness.lol/</loc>", "sitemap.xml")

    print("LIVE_SMOKE_OK=true")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
