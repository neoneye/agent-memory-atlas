"""Cheap metadata, collected without cloning anything.

Every number here carries a coverage label beside it, and the labels are the
point. `complete` means the endpoint returned the whole thing. `sampled` means a
page was read and there are more. `unavailable` means the request failed, and
`budget_exceeded` means it was never made. An unknown count is `None` — never
zero, because zero is a measurement and this is the absence of one.

Three things the specification asks not to be confused, kept apart here:

* The **owner account's age** measures an account. It is not developer
  experience, and a new account is a caution, not a spam label.
* **Public repository ownership** is not the same as contributing elsewhere, and
  private history is unavailable rather than absent.
* **Issues and pull requests** are both issues to GitHub's counter. The open
  issue count is corrected by a separate pull-request count, and when that
  correction cannot be made the count stays labelled as including PRs.
"""

from __future__ import annotations

import re
from typing import Any

from fetching import BUDGET, Client, FetchError, RepoBudget, api_url

# Names that are automation. Kept explicit and separate from the honest
# statement that follows it: GitHub's account type does not prove that the
# remainder is a person, so the remainder is "apparently non-bot", not "human".
BOT_SUFFIXES = ("[bot]", "-bot", "_bot")
KNOWN_BOTS = {
    "dependabot", "dependabot-preview", "renovate", "renovate-bot", "greenkeeper",
    "github-actions", "imgbot", "allcontributors", "codecov", "snyk-bot",
    "pre-commit-ci", "mergify", "stale", "semantic-release-bot", "copilot",
    "restyled-io", "whitesource-bolt-for-github", "deepsource-autofix",
}
LINK_LAST = re.compile(r'<[^>]*[?&]page=(\d+)[^>]*>;\s*rel="last"')


def is_bot(login: str | None, account_type: str | None = None) -> bool:
    if not login:
        return False
    name = login.lower()
    if account_type == "Bot":
        return True
    if name in KNOWN_BOTS:
        return True
    return any(name.endswith(suffix) for suffix in BOT_SUFFIXES)


def _page_count(headers: dict[str, str], page_items: int, per_page: int) -> tuple[int | None, str]:
    """Turn a paginated response into a count and its coverage.

    With a `rel="last"` link the total is a lower bound of `(last-1)*per_page`;
    reporting that as an exact figure would be a fabrication, so it is reported
    as a floor with `sampled` coverage. Without the link, one page is all there
    is and the count is exact.
    """
    link = headers.get("link", "")
    match = LINK_LAST.search(link)
    if match:
        last = int(match.group(1))
        return (last - 1) * per_page + (1 if page_items else 0), "sampled"
    return page_items, "complete"


class Collector:
    def __init__(self, client: Client):
        self.client = client
        self._owners: dict[str, tuple[dict | None, str]] = {}

    def _get(self, url: str, budget: RepoBudget, *, cache: bool = True):
        return self.client.get(url, cache=cache, repo_budget=budget,
                               max_bytes=self.client.limits.tree_bytes)

    # --- repository -------------------------------------------------------
    def repository(self, owner: str, name: str, budget: RepoBudget) -> tuple[dict, dict]:
        facts: dict[str, Any] = {}
        coverage: dict[str, str] = {}
        try:
            payload = self._get(api_url("repos", owner, name), budget).json()
        except FetchError as error:
            return {}, {"repository": _coverage_for(error)}

        facts.update(
            github_repo_id=payload.get("id"),
            full_name=payload.get("full_name"),
            default_branch=payload.get("default_branch"),
            description=payload.get("description"),
            language=payload.get("language"),
            topics=payload.get("topics") or [],
            stars=payload.get("stargazers_count"),
            forks=payload.get("forks_count"),
            watchers=payload.get("subscribers_count"),
            open_issues_including_prs=payload.get("open_issues_count"),
            size_kb=payload.get("size"),
            created_at=payload.get("created_at"),
            pushed_at=payload.get("pushed_at"),
            updated_at=payload.get("updated_at"),
            archived=payload.get("archived"),
            disabled=payload.get("disabled"),
            is_fork=payload.get("fork"),
            parent=(payload.get("parent") or {}).get("full_name"),
            license=(payload.get("license") or {}).get("spdx_id"),
            has_issues=payload.get("has_issues"),
            owner_login=(payload.get("owner") or {}).get("login"),
            owner_type=(payload.get("owner") or {}).get("type"),
        )
        coverage["repository"] = "complete"
        return facts, coverage

    def open_pulls(self, owner: str, name: str, budget: RepoBudget) -> tuple[dict, dict]:
        try:
            response = self._get(
                api_url("repos", owner, name, "pulls", state="open", per_page=1), budget
            )
            items = response.json()
            count, coverage = _page_count(response.headers, len(items), 1)
            return {"open_pull_requests": count}, {"open_pull_requests": coverage}
        except FetchError as error:
            return {"open_pull_requests": None}, {"open_pull_requests": _coverage_for(error)}

    def contributors(self, owner: str, name: str, budget: RepoBudget) -> tuple[dict, dict]:
        try:
            response = self._get(
                api_url("repos", owner, name, "contributors", per_page=100, anon="0"), budget
            )
            items = response.json()
        except FetchError as error:
            category = _coverage_for(error)
            if error.category == "unavailable":
                # An empty repository answers 409 here. That is a fact, not a gap.
                return ({"contributors_total": 0, "contributors_bot": 0,
                         "contributors_apparently_non_bot": 0},
                        {"contributors": "complete"})
            return ({"contributors_total": None, "contributors_bot": None,
                     "contributors_apparently_non_bot": None}, {"contributors": category})

        if not isinstance(items, list):
            return {"contributors_total": None}, {"contributors": "unavailable"}
        bots = [entry for entry in items if is_bot(entry.get("login"), entry.get("type"))]
        _, coverage = _page_count(response.headers, len(items), 100)
        return (
            {
                "contributors_total": len(items),
                "contributors_bot": len(bots),
                "contributors_apparently_non_bot": len(items) - len(bots),
                "contributors_top": [
                    {"login": entry.get("login"), "commits": entry.get("contributions"),
                     "bot": is_bot(entry.get("login"), entry.get("type"))}
                    for entry in items[:10]
                ],
            },
            {"contributors": coverage},
        )

    def commit_sample(self, owner: str, name: str, branch: str | None,
                      budget: RepoBudget) -> tuple[dict, dict]:
        """One page of recent commits: the head sha, the span they cover, and who
        wrote them. Not an exact commit count — paginating every commit to get one
        is exactly the crawl this program is not allowed to do."""
        try:
            response = self._get(
                api_url("repos", owner, name, "commits", sha=branch, per_page=100), budget,
                cache=False,
            )
            items = response.json()
        except FetchError as error:
            if error.category == "unavailable":
                return ({"head_commit": None, "commit_sample": 0, "empty_repository": True},
                        {"commits": "complete"})
            return ({"head_commit": None, "commit_sample": None},
                    {"commits": _coverage_for(error)})

        if not isinstance(items, list) or not items:
            return ({"head_commit": None, "commit_sample": 0}, {"commits": "complete"})

        dates = [
            (entry.get("commit") or {}).get("author", {}).get("date")
            for entry in items
            if (entry.get("commit") or {}).get("author", {}).get("date")
        ]
        authors = {
            (entry.get("author") or {}).get("login")
            for entry in items
            if (entry.get("author") or {}).get("login")
        }
        bot_authors = {login for login in authors if is_bot(login)}
        _, coverage = _page_count(response.headers, len(items), 100)
        return (
            {
                "head_commit": items[0].get("sha"),
                "commit_sample": len(items),
                "commit_sample_newest": max(dates) if dates else None,
                "commit_sample_oldest": min(dates) if dates else None,
                "commit_authors_apparently_non_bot": len(authors - bot_authors),
                "commit_authors_bot": len(bot_authors),
            },
            {"commits": coverage},
        )

    def merged_external_pulls(self, owner: str, name: str, budget: RepoBudget) -> tuple[dict, dict]:
        """Merged pull requests whose author is not the repository owner.

        A reviewed, merged change from outside is the participation signal worth
        having; a raw contribution total is not, because a fork's copied history
        and a week of dependency bumps both inflate it.
        """
        try:
            response = self._get(
                api_url("repos", owner, name, "pulls", state="closed", per_page=30,
                        sort="updated", direction="desc"),
                budget, cache=False,
            )
            items = response.json()
        except FetchError as error:
            return ({"merged_external_pulls": None}, {"pulls": _coverage_for(error)})
        if not isinstance(items, list):
            return ({"merged_external_pulls": None}, {"pulls": "unavailable"})
        merged = [entry for entry in items if entry.get("merged_at")]
        external = [
            entry for entry in merged
            if (entry.get("user") or {}).get("login", "").lower() != owner.lower()
            and not is_bot((entry.get("user") or {}).get("login"),
                           (entry.get("user") or {}).get("type"))
        ]
        return (
            {
                "closed_pulls_sampled": len(items),
                "merged_pulls_sampled": len(merged),
                "merged_external_pulls": len(external),
            },
            {"pulls": "sampled" if len(items) >= 30 else "complete"},
        )

    def owner(self, login: str, budget: RepoBudget) -> tuple[dict, dict]:
        """One lookup per owner per run, shared by every candidate they own."""
        if login in self._owners:
            payload, coverage = self._owners[login]
        else:
            try:
                payload = self._get(api_url("users", login), budget).json()
                coverage = "complete"
            except FetchError as error:
                payload, coverage = None, _coverage_for(error)
            self._owners[login] = (payload, coverage)

        if payload is None:
            return ({"owner_created_at": None, "owner_public_repos": None}, {"owner": coverage})
        return (
            {
                "owner_created_at": payload.get("created_at"),
                "owner_public_repos": payload.get("public_repos"),
                "owner_followers": payload.get("followers"),
                "owner_account_type": payload.get("type"),
                "owner_is_bot_account": is_bot(payload.get("login"), payload.get("type")),
                # Stated as what it is: the count of repositories this account
                # owns publicly. Contributions elsewhere are not this number, and
                # private work is unavailable rather than absent.
                "owner_public_repos_is_not_contribution_count": True,
            },
            {"owner": coverage},
        )


def _coverage_for(error: FetchError) -> str:
    if error.category == BUDGET:
        return "budget_exceeded"
    return "unavailable"


def collect(collector: Collector, owner: str, name: str, budget: RepoBudget) -> tuple[dict, dict]:
    """Everything above, in one pass, with per-repository failures isolated."""
    facts: dict[str, Any] = {}
    coverage: dict[str, str] = {}
    for chunk_facts, chunk_coverage in [collector.repository(owner, name, budget)]:
        facts.update(chunk_facts)
        coverage.update(chunk_coverage)
    if coverage.get("repository") != "complete":
        return facts, coverage

    branch = facts.get("default_branch")
    for getter in (
        lambda: collector.open_pulls(owner, name, budget),
        lambda: collector.contributors(owner, name, budget),
        lambda: collector.commit_sample(owner, name, branch, budget),
        lambda: collector.merged_external_pulls(owner, name, budget),
        lambda: collector.owner(facts.get("owner_login") or owner, budget),
    ):
        chunk_facts, chunk_coverage = getter()
        facts.update(chunk_facts)
        coverage.update(chunk_coverage)

    # The correction GitHub's own field does not make for you.
    issues = facts.get("open_issues_including_prs")
    pulls = facts.get("open_pull_requests")
    if issues is not None and pulls is not None:
        facts["open_issues_excluding_prs"] = max(issues - pulls, 0)
    else:
        facts["open_issues_excluding_prs"] = None
    return facts, coverage
