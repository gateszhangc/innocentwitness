#!/usr/bin/env python3

import argparse
import json
import os
import sys
import time
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


API_BASE = "https://api.porkbun.com/api/json/v3"
RETRYABLE_STATUS_CODES = {502, 503, 504}
MAX_ATTEMPTS = 5


def credentials() -> tuple[str, str]:
    api_key = os.environ.get("PORKBUN_API_KEY")
    secret_key = os.environ.get("PORKBUN_SECRET_API_KEY")
    if not api_key or not secret_key:
        raise SystemExit("PORKBUN_API_KEY and PORKBUN_SECRET_API_KEY must be set.")
    return api_key, secret_key


def api_post(path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    api_key, secret_key = credentials()
    body = {
        "apikey": api_key,
        "secretapikey": secret_key,
    }
    if payload:
        body.update(payload)

    request = Request(
        f"{API_BASE}/{path.lstrip('/')}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            if error.code in RETRYABLE_STATUS_CODES and attempt < MAX_ATTEMPTS:
                time.sleep(attempt)
                continue
            raise SystemExit(f"Porkbun API request failed: {error.code} {details}") from error


def retrieve_by_name_type(domain: str, record_type: str, name: str) -> list[dict[str, Any]]:
    pieces = ["dns", "retrieveByNameType", quote(domain), quote(record_type)]
    if name:
        pieces.append(quote(name))
    response = api_post("/".join(pieces))
    return response.get("records", [])


def create_record(domain: str, name: str, record_type: str, content: str, ttl: str = "600") -> dict[str, Any]:
    return api_post(
        f"dns/create/{quote(domain)}",
        {
            "name": name,
            "type": record_type,
            "content": content,
            "ttl": ttl,
        },
    )


def delete_record(domain: str, record_id: str) -> dict[str, Any]:
    return api_post(f"dns/delete/{quote(domain)}/{quote(record_id)}")


def ensure_a_record(domain: str, name: str, content: str, ttl: str) -> None:
    existing = retrieve_by_name_type(domain, "A", name)
    if len(existing) == 1 and existing[0].get("content") == content:
        print(f"A record already set: {domain} {name or '@'} -> {content}")
        return

    for record in existing:
        delete_record(domain, str(record["id"]))

    response = create_record(domain, name, "A", content, ttl=ttl)
    if response.get("status") != "SUCCESS":
        raise SystemExit(f"Failed to create A record: {response}")
    print(f"A record set: {domain} {name or '@'} -> {content}")


def ensure_txt_record(domain: str, name: str, content: str, ttl: str) -> None:
    existing = retrieve_by_name_type(domain, "TXT", name)
    if any(record.get("content") == content for record in existing):
        print(f"TXT record already present: {domain} {name or '@'} -> {content}")
        return

    response = create_record(domain, name, "TXT", content, ttl=ttl)
    if response.get("status") != "SUCCESS":
        raise SystemExit(f"Failed to create TXT record: {response}")
    print(f"TXT record created: {domain} {name or '@'} -> {content}")


def list_records(domain: str) -> None:
    response = api_post(f"dns/retrieve/{quote(domain)}")
    print(json.dumps(response, ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage Porkbun DNS records for innocentwitness.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List all records for a domain")
    list_parser.add_argument("--domain", required=True)

    a_parser = subparsers.add_parser("ensure-a", help="Ensure a single root/subdomain A record exists")
    a_parser.add_argument("--domain", required=True)
    a_parser.add_argument("--name", default="")
    a_parser.add_argument("--content", required=True)
    a_parser.add_argument("--ttl", default="600")

    txt_parser = subparsers.add_parser("ensure-txt", help="Ensure a TXT record exists")
    txt_parser.add_argument("--domain", required=True)
    txt_parser.add_argument("--name", default="")
    txt_parser.add_argument("--content", required=True)
    txt_parser.add_argument("--ttl", default="600")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "list":
        list_records(args.domain)
        return 0

    if args.command == "ensure-a":
        ensure_a_record(args.domain, args.name, args.content, args.ttl)
        return 0

    if args.command == "ensure-txt":
        ensure_txt_record(args.domain, args.name, args.content, args.ttl)
        return 0

    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
