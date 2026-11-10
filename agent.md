# Working rules for this repository

The rules for all shrippen repositories are in `RULES.md` (writing, code, commits, bug
fixes, repository, GUI). It is a synced copy from the rules repository; do not edit it
here. This file holds only what is particular to this repository. A Claude Code session on
the owner's machine has the rules through the global `CLAUDE.md` already and reads
`RULES.md` only for its GUI rule, before work on a user interface.

## Rules of this project

- For bug fixes on hardware:
  - Display and timing bugs need the Pi with the panel. There the test is a script checked
    into `tests/` that shows the failure on the hardware; it stays in the repo, and its output
    goes in the commit or PR. What runs without the panel gets a normal unit test. The
    repository has no tests yet: the first one creates `tests/`.

## Repository (this project)

- Everything else: `RULES.md` (Repository) and the skill `pr-review`.
