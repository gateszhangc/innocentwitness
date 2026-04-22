#!/usr/bin/env python3

import argparse
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the K8s image build job manifest.")
    parser.add_argument("--template", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--job-name", required=True)
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--app-name", required=True)
    parser.add_argument("--service-account-name", required=True)
    parser.add_argument("--git-secret-name", required=True)
    parser.add_argument("--git-token-key", required=True)
    parser.add_argument("--registry-secret-name", required=True)
    parser.add_argument("--github-repository", required=True)
    parser.add_argument("--git-ref", required=True)
    parser.add_argument("--git-sha", required=True)
    parser.add_argument("--image-name", required=True)
    parser.add_argument("--image-tag", required=True)
    parser.add_argument("--cache-repo", required=True)
    parser.add_argument("--dockerfile-path", required=True)
    parser.add_argument("--ttl-seconds", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    template = Path(args.template).read_text()
    replacements = {
        "JOB_NAME": args.job_name,
        "BUILD_NAMESPACE": args.namespace,
        "APP_NAME": args.app_name,
        "SERVICE_ACCOUNT_NAME": args.service_account_name,
        "GIT_SECRET_NAME": args.git_secret_name,
        "GIT_TOKEN_KEY": args.git_token_key,
        "REGISTRY_SECRET_NAME": args.registry_secret_name,
        "GITHUB_REPOSITORY": args.github_repository,
        "GIT_REF": args.git_ref,
        "GIT_SHA": args.git_sha,
        "IMAGE_NAME": args.image_name,
        "IMAGE_TAG": args.image_tag,
        "CACHE_REPO": args.cache_repo,
        "DOCKERFILE_PATH": args.dockerfile_path,
        "TTL_SECONDS": args.ttl_seconds,
    }

    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)

    unresolved = sorted(set(re.findall(r"{{([A-Z0-9_]+)}}", rendered)))
    if unresolved:
        raise SystemExit(f"Unresolved placeholders: {', '.join(unresolved)}")

    Path(args.output).write_text(rendered)


if __name__ == "__main__":
    main()
