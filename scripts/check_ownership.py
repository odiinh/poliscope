"""Check the current task branch against the folder ownership in docs/PLAN.md."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNERS = {
    "a": ("pipeline/ingest/", "data/raw/", "data/interim/ingest/", "docs/status/a.md"),
    "b": (
        "pipeline/extract/",
        "contracts/prompt/",
        "data/interim/extract/",
        "app/src/app/api/extract/",
        "docs/status/b.md",
    ),
    "c": (
        "pipeline/model/",
        "data/public/",
        "docs/pitch_numbers.md",
        "docs/status/c.md",
    ),
}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def owner(path):
    for role, paths in OWNERS.items():
        if any(
            path.startswith(entry) if entry.endswith("/") else path == entry
            for entry in paths
        ):
            return role
    return "d"


def main():
    branch = git("branch", "--show-current").strip()
    role, separator, _ = branch.partition("/")
    if not separator or role not in ("a", "b", "c", "d"):
        return 0
    base = git("merge-base", "origin/main", "HEAD").strip()
    tracked = git("diff", "--no-renames", "--name-only", "-z", base).split("\0")
    untracked = git("ls-files", "--others", "--exclude-standard", "-z").split("\0")
    violations = sorted(
        {path for path in tracked + untracked if path and owner(path) != role}
    )
    for path in violations:
        print(
            f"{branch} cannot change {path} (member {owner(path).upper()})",
            file=sys.stderr,
        )
    return int(bool(violations))


if __name__ == "__main__":
    sys.exit(main())
