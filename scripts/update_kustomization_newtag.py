#!/usr/bin/env python3

import argparse
import re
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update the newTag for a named image inside a kustomization.yaml file."
    )
    parser.add_argument("--file", required=True, help="Path to the kustomization.yaml file")
    parser.add_argument("--image", required=True, help="Image name to update")
    parser.add_argument("--new-tag", required=True, help="Tag value to write")
    return parser.parse_args()


def update_kustomization(content: str, image_name: str, new_tag: str) -> str:
    lines = content.splitlines()
    images_indent = None
    in_images = False
    item_start = None
    item_name = None
    target_found = False

    def finalize_item(end_index: int) -> None:
        nonlocal lines, item_start, item_name, target_found
        if item_start is None or item_name != image_name:
            item_start = None
            item_name = None
            return

        target_found = True
        item_lines = lines[item_start:end_index]
        new_tag_index = None
        insert_index = item_start + 1

        for offset, line in enumerate(item_lines):
            absolute_index = item_start + offset
            if re.match(r"^\s*newName:\s*", line):
                insert_index = absolute_index + 1
            if re.match(r"^\s*newTag:\s*", line):
                new_tag_index = absolute_index
                break

        if new_tag_index is not None:
            indent = re.match(r"^(\s*)", lines[new_tag_index]).group(1)
            lines[new_tag_index] = f"{indent}newTag: {new_tag}"
        else:
            name_line = lines[item_start]
            indent_match = re.match(r"^(\s*)-\s+name:\s*", name_line)
            indent = f"{indent_match.group(1)}  " if indent_match else "    "
            lines.insert(insert_index, f"{indent}newTag: {new_tag}")

        item_start = None
        item_name = None

    for index, line in enumerate(lines):
        if not in_images:
            match = re.match(r"^(\s*)images:\s*$", line)
            if match:
                images_indent = len(match.group(1))
                in_images = True
            continue

        stripped = line.strip()
        current_indent = len(line) - len(line.lstrip(" "))

        if stripped and current_indent <= images_indent and not line.lstrip().startswith("#"):
            finalize_item(index)
            in_images = False
            images_indent = None
            continue

        item_match = re.match(r"^(\s*)-\s+name:\s*(\S.*?)\s*$", line)
        if item_match:
            finalize_item(index)
            item_start = index
            item_name = item_match.group(2).strip().strip("\"'")

    finalize_item(len(lines))

    if not target_found:
        raise ValueError(f"Could not find image '{image_name}' in images section.")

    return "".join(f"{line}\n" for line in lines)


def main() -> int:
    args = parse_args()
    path = Path(args.file)
    original = path.read_text()
    updated = update_kustomization(original, args.image, args.new_tag)

    if updated != original:
        path.write_text(updated)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(error, file=sys.stderr)
        sys.exit(1)
