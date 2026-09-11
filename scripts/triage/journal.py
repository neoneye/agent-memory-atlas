"""A bounded, redacted run log.

One JSON line per command, appended to `<state-dir>/triage.log`, rotated at the
configured ceiling with exactly one `.1` kept behind it. Two lines per run at
most, so the file grows with invocations rather than with the feed.

Everything written goes through `redact` first. The rule upstream is that tokens
never enter these strings at all; this is the second line of defence, for the
message this program did not compose itself — a URL echoed back by an API, an
error from a library.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from util import dumps, iso, redact, utc_now


def write(path: Path, event: str, payload: dict[str, Any], *, max_bytes: int) -> None:
    """Append one event. Failures here never fail a command.

    A log that can abort a run is worse than no log: the decision has already
    been committed to the database by the time anything is written here.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        _rotate(path, max_bytes)
        line = redact(dumps({"at": iso(utc_now()), "event": event, **payload})) + "\n"
        with path.open("a", encoding="utf-8") as stream:
            stream.write(line)
        os.chmod(path, 0o600)
    except OSError:
        return


def _rotate(path: Path, max_bytes: int) -> None:
    """Half the ceiling per file, two files: the live one and one predecessor."""
    try:
        if not path.exists() or path.stat().st_size < max_bytes // 2:
            return
    except OSError:
        return
    previous = path.with_suffix(path.suffix + ".1")
    previous.unlink(missing_ok=True)
    path.replace(previous)


def tail(path: Path, lines: int = 10) -> list[str]:
    if not path.is_file():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:]
