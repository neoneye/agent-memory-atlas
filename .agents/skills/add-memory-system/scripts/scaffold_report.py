#!/usr/bin/env python3
"""Scaffold a commit-pinned Agent Memory Atlas system report."""

from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


SECTION_TITLES = (
    "1. Executive Summary",
    "2. Mental Model",
    "3. Architecture",
    "4. Essential Implementation Paths",
    "5. Memory Data Model",
    "6. Retrieval Mechanics",
    "7. Write Mechanics",
    "8. Agent Integration",
    "9. Reliability, Safety, and Trust",
    "10. Tests, Evals, and Benchmarks",
    "11. Patterns Worth Stealing",
    "12. Antipatterns / Risks",
    "13. Build-vs-Borrow Takeaways",
    "14. Open Questions",
    "Appendix: File Index",
)


class ScaffoldError(RuntimeError):
    """A user-correctable scaffolding error."""


def git(repository: Path, *arguments: str) -> str:
    command = ("git", "-C", str(repository), *arguments)
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise ScaffoldError("git is required but was not found") from error
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip()
        raise ScaffoldError(
            f"Git command failed in {repository}: {detail or 'unknown error'}"
        ) from error
    return result.stdout.strip()


def normalize_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    if not slug:
        raise ScaffoldError("The report slug must contain a letter or digit")
    return slug


def normalize_repository_url(remote: str) -> str:
    value = remote.strip()
    scp_match = re.fullmatch(r"git@github\.com:([^/]+)/(.+)", value)
    if scp_match:
        owner, repository = scp_match.groups()
        return f"https://github.com/{owner}/{repository.removesuffix('.git')}"

    ssh_match = re.fullmatch(r"ssh://git@github\.com/([^/]+)/(.+)", value)
    if ssh_match:
        owner, repository = ssh_match.groups()
        return f"https://github.com/{owner}/{repository.removesuffix('.git')}"

    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc.lower() == "github.com":
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) >= 2:
            return (
                f"https://github.com/{parts[0]}/"
                f"{parts[1].removesuffix('.git')}"
            )

    raise ScaffoldError(
        "Could not derive a public GitHub URL from origin. "
        "Pass --source-url explicitly."
    )


def source_name(source_url: str) -> str:
    parsed = urlparse(source_url)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise ScaffoldError(
            "--source-url must include an owner and repository name"
        )
    return f"{parts[0]}/{parts[1].removesuffix('.git')}"


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


# Keep in step with COLUMNS in scripts/generate_matrix.py.
MATRIX_KEYS = (
    "memory_unit",
    "storage",
    "retrieval",
    "write",
    "update_delete",
    "scoping",
    "integration",
    "background",
    "trust",
    "strengths",
    "risks",
)


def render_report(
    *,
    title: str,
    eyebrow: str,
    description: str,
    repository_name: str,
    repository_url: str,
    revision: str,
    analyzed_at: str,
) -> str:
    frontmatter = (
        "---\n"
        f"title: {yaml_string(title)}\n"
        f"eyebrow: {yaml_string(eyebrow)}\n"
        f"description: {yaml_string(description)}\n"
        "root: ../..\n"
        "page_kind: system\n"
        f"source_name: {yaml_string(repository_name)}\n"
        f"source_url: {repository_url}\n"
        f"revision: {revision}\n"
        f"revision_url: {repository_url}/commit/{revision}\n"
        f"analyzed_at: {analyzed_at}\n"
        # Both blocks are required. generate_matrix.py fails the build if the
        # matrix block is absent or incomplete, and if `capabilities` is
        # missing entirely — an empty string means "assessed, carries none",
        # which is a different claim from "nobody looked".
        'capabilities: ""\n'
        "matrix:\n"
        + "".join(f'  {key}: ""\n' for key in MATRIX_KEYS)
        + "---\n"
    )
    sections = "\n".join(
        f"\n## {section}\n\n<!-- Replace with code-grounded analysis. -->\n"
        for section in SECTION_TITLES
    )
    return frontmatter + sections


def default_atlas_root() -> Path:
    return Path(__file__).resolve().parents[4]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create content/systems/<slug>.md using a local repository's "
            "origin and exact HEAD commit."
        )
    )
    parser.add_argument(
        "repository",
        type=Path,
        help="Local checkout of the memory-system repository",
    )
    parser.add_argument("--slug", required=True, help="Report filename slug")
    parser.add_argument("--title", required=True, help="Display title")
    parser.add_argument("--eyebrow", required=True, help="Architecture label")
    parser.add_argument(
        "--description",
        required=True,
        help="One-sentence architecture description",
    )
    parser.add_argument(
        "--source-url",
        help="Public repository URL; defaults to normalized origin",
    )
    parser.add_argument(
        "--atlas-root",
        type=Path,
        default=default_atlas_root(),
        help="Agent Memory Atlas root (normally detected automatically)",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the report without creating a file",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    repository = arguments.repository.expanduser().resolve()
    atlas_root = arguments.atlas_root.expanduser().resolve()

    try:
        if not repository.is_dir():
            raise ScaffoldError(f"Repository directory does not exist: {repository}")
        if not (atlas_root / "content" / "systems").is_dir():
            raise ScaffoldError(
                f"Atlas root does not contain content/systems: {atlas_root}"
            )

        checkout_root = Path(git(repository, "rev-parse", "--show-toplevel")).resolve()
        if checkout_root != repository:
            repository = checkout_root

        revision = git(repository, "rev-parse", "HEAD")
        if not re.fullmatch(r"[0-9a-fA-F]{40,64}", revision):
            raise ScaffoldError(f"Unexpected commit ID returned by git: {revision}")

        if arguments.source_url:
            repository_url = arguments.source_url.rstrip("/").removesuffix(".git")
        else:
            repository_url = normalize_repository_url(
                git(repository, "remote", "get-url", "origin")
            )

        text_fields = {
            "title": arguments.title.strip(),
            "eyebrow": arguments.eyebrow.strip(),
            "description": arguments.description.strip(),
        }
        empty_fields = [name for name, value in text_fields.items() if not value]
        if empty_fields:
            raise ScaffoldError(
                "These fields cannot be empty: " + ", ".join(empty_fields)
            )

        name = source_name(repository_url)
        slug = normalize_slug(arguments.slug)
        report = render_report(
            title=text_fields["title"],
            eyebrow=text_fields["eyebrow"],
            description=text_fields["description"],
            repository_name=name,
            repository_url=repository_url,
            revision=revision,
            analyzed_at=datetime.date.today().isoformat(),
        )

        if arguments.stdout:
            print(report, end="")
            return 0

        destination = atlas_root / "content" / "systems" / f"{slug}.md"
        if destination.exists():
            raise ScaffoldError(
                f"Refusing to overwrite existing report: {destination}"
            )
        destination.write_text(report, encoding="utf-8")
        print(
            f"Created {destination}\n"
            f"Source: {repository_url}\n"
            f"Revision: {revision}"
        )
        return 0
    except ScaffoldError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
