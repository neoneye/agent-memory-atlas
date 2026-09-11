"""Configuration: defaults, a JSON file, environment, then command-line flags.

Every path the program touches is resolved here. Two rules are load-bearing.
No maintainer's filesystem path is baked into the code — the state directory has
a default under `$XDG_DATA_HOME`, and everything else hangs off it or off the
repository the CLI was run from. And the upstream source is configuration, not a
constant: the maintainer's fork is a contingency that requires an explicit
change, never an automatic fallback when Daily-Nerd's copy is unreachable.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, fields, asdict
from pathlib import Path
from typing import Any

from util import loads

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = Path(__file__).resolve().parent

ENV_PREFIX = "AMA_TRIAGE_"


def _default_state_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME")
    root = Path(base) if base else Path.home() / ".local" / "share"
    return root / "agent-memory-atlas-triage"


@dataclass
class Limits:
    """Section 7 of the specification, in one place so no collector can invent
    its own ceiling. These are application ceilings, not a promise that the
    whole feed can be inspected in a day."""

    feed_bytes: int = 16 * 1024 * 1024
    blob_bytes: int = 256 * 1024
    blobs_per_repo: int = 12
    source_text_bytes_per_repo: int = 2 * 1024 * 1024
    tree_bytes: int = 10 * 1024 * 1024
    response_bytes_per_repo: int = 16 * 1024 * 1024
    requests_per_repo: int = 30
    requests_per_day: int = 3000
    concurrent_assessments: int = 1
    assessment_seconds: int = 90
    classifier_calls_per_repo: int = 2
    classifier_input_tokens: int = 12000
    classifier_output_tokens: int = 2000
    classifier_calls_per_day: int = 400
    connect_timeout: float = 5.0
    read_timeout: float = 20.0
    cache_bytes: int = 64 * 1024 * 1024
    cache_ttl_days: int = 7
    scratch_bytes: int = 32 * 1024 * 1024
    log_bytes: int = 16 * 1024 * 1024
    state_bytes: int = 256 * 1024 * 1024
    excerpt_chars: int = 600
    quarantine_lines: int = 20


@dataclass
class Config:
    # --- where state lives
    state_dir: Path = field(default_factory=_default_state_dir)
    output_dir: Path = field(default_factory=lambda: REPO_ROOT / "scout")
    atlas_repo: Path = REPO_ROOT

    # --- the upstream feed
    source_kind: str = "github"                     # github | file
    source_repo: str = "Daily-Nerd/scout"
    source_ref: str = "main"
    source_path: str = "data/candidates.jsonl"
    source_file: Path | None = None                 # explicit local override

    # --- capacity
    timezone: str = "Europe/Copenhagen"
    daily_admissions: int = 20
    outstanding_capacity: int = 20
    inspection_budget: int = 100
    metadata_budget: int = 400
    # Measured metadata older than this is due for a refresh under the same budget.
    metadata_max_age_days: int = 14
    exploration_share: float = 0.20
    minimum_score: int = 60
    assessment_max_age_days: int = 7
    lease_seconds: int = 4 * 3600

    # --- optional classifier
    classifier_provider: str | None = None          # None = rules only
    classifier_model: str | None = None
    classifier_base_url: str | None = None

    # --- credentials, never stored and never exported
    github_token: str | None = None
    classifier_token: str | None = None

    policy_file: Path = PACKAGE_ROOT / "policy.json"
    limits: Limits = field(default_factory=Limits)
    user_agent: str = "agent-memory-atlas-triage/1 (+https://github.com/neoneye/agent-memory-atlas)"

    # --- derived ------------------------------------------------------------
    @property
    def db_path(self) -> Path:
        return self.state_dir / "triage.sqlite3"

    @property
    def scratch_root(self) -> Path:
        return self.state_dir / "scratch"

    @property
    def lock_path(self) -> Path:
        return self.state_dir / "triage.lock"

    @property
    def log_path(self) -> Path:
        return self.state_dir / "triage.log"

    @property
    def source_identity(self) -> str:
        if self.source_kind == "file":
            return f"file:{self.source_file}"
        return f"github:{self.source_repo}@{self.source_ref}:{self.source_path}"

    def redacted(self) -> dict[str, Any]:
        """The shape shown by `status` and written into reports. Credentials are
        reported as present or absent and never by value."""
        data: dict[str, Any] = {}
        for entry in fields(self):
            if entry.name in {"github_token", "classifier_token"}:
                data[entry.name] = "set" if getattr(self, entry.name) else "unset"
                continue
            value = getattr(self, entry.name)
            if isinstance(value, Path):
                value = str(value)
            elif isinstance(value, Limits):
                value = asdict(value)
            data[entry.name] = value
        return data


_PATHS = {"state_dir", "output_dir", "atlas_repo", "source_file", "policy_file"}
_INTS = {
    "daily_admissions", "outstanding_capacity", "inspection_budget", "metadata_budget", "metadata_max_age_days",
    "minimum_score", "assessment_max_age_days", "lease_seconds",
}
_FLOATS = {"exploration_share"}


def _coerce(name: str, raw: Any) -> Any:
    if name in _PATHS:
        return Path(raw).expanduser() if raw is not None else None
    if name in _INTS:
        return int(raw)
    if name in _FLOATS:
        return float(raw)
    return raw


def load(overrides: dict[str, Any] | None = None) -> Config:
    """Defaults, then the config file, then the environment, then flags.

    The config file is looked for at `$AMA_TRIAGE_CONFIG`, else inside the state
    directory the earlier layers resolved to — so pointing the state directory
    somewhere else also moves its configuration.
    """
    config = Config()
    overrides = dict(overrides or {})

    env_state = os.environ.get(ENV_PREFIX + "STATE_DIR")
    if env_state:
        config.state_dir = Path(env_state).expanduser()
    if overrides.get("state_dir"):
        config.state_dir = Path(overrides["state_dir"]).expanduser()

    config_file = os.environ.get(ENV_PREFIX + "CONFIG")
    path = Path(config_file).expanduser() if config_file else config.state_dir / "config.json"
    if path.is_file():
        raw = loads(path.read_text(encoding="utf-8"))
        limits_raw = raw.pop("limits", {})
        for key, value in raw.items():
            if hasattr(config, key):
                setattr(config, key, _coerce(key, value))
        for key, value in limits_raw.items():
            if hasattr(config.limits, key):
                setattr(config.limits, key, value)

    known = {entry.name for entry in fields(Config)} - {"limits"}
    for key in known:
        env_value = os.environ.get(ENV_PREFIX + key.upper())
        if env_value not in (None, ""):
            setattr(config, key, _coerce(key, env_value))
    for key in {entry.name for entry in fields(Limits)}:
        env_value = os.environ.get(ENV_PREFIX + "LIMIT_" + key.upper())
        if env_value not in (None, ""):
            current = getattr(config.limits, key)
            setattr(config.limits, key, type(current)(env_value))

    if config.github_token is None:
        config.github_token = os.environ.get("GITHUB_TOKEN") or None
    if config.classifier_token is None:
        config.classifier_token = os.environ.get(ENV_PREFIX + "CLASSIFIER_TOKEN") or None

    for key, value in overrides.items():
        if value is None or not hasattr(config, key):
            continue
        setattr(config, key, _coerce(key, value))

    if config.source_file is not None and overrides.get("source_file"):
        config.source_kind = "file"
    return config
