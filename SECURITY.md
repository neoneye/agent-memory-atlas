# Security policy

## Reporting a vulnerability

Email **Simon Strandgaard** at **neoneye@gmail.com**, or use GitHub's
[private vulnerability reporting](https://github.com/neoneye/agent-memory-atlas/security/advisories/new)
(the repository's **Security** tab, then **Report a vulnerability**). Please do
not open a public issue for a vulnerability.

Include what you found, where (a file, a page URL or a commit), and how to
reproduce it. If you would like to be credited when it is fixed, say how.

## What is in scope

- **The published site**,
  [neoneye.github.io/agent-memory-atlas](https://neoneye.github.io/agent-memory-atlas/):
  script injection, content that runs or loads something it should not, and the
  analytics consent flow.
- **The scripts in this repository that handle third-party code**: a way to make
  `scripts/screen_repo.py` miss an auto-executing surface, or any script that
  executes code from a repository it was only meant to read.
- **The source archive**, the `agent-memory-atlas-archive` organisation: a copy
  that runs the upstream's CI, or a pin that points somewhere it should not.
- **Something published by mistake**: a secret, a token or personal data that a
  report, note or archive copy reproduces from an analysed repository.

Only the current `main` branch and the site built from it are supported.

## What is not in scope

Vulnerabilities in the memory systems the atlas analyses belong to those
projects. Report them through the project's own security policy, usually its
`SECURITY.md`; many ask for a private channel rather than a public issue. The
atlas does not relay reports to upstream projects.
