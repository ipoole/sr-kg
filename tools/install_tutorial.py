#!/usr/bin/env python3
"""Validate and install an exported tutorial as a built-in, ready for Git review."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from srkg.tutorial_packages import install_tutorial
from srkg.tutorials import TutorialLoadError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    parser.add_argument("--tutorial-id", required=True)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--domains", nargs="+")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        target = install_tutorial(args.package, args.data_root, args.tutorial_id,
                                  replace=args.replace, domains=args.domains, dry_run=args.dry_run)
    except (OSError, TutorialLoadError) as error:
        parser.exit(1, str(error) + "\n")
    print(("Validated; would update " if args.dry_run else "Installed into ") + str(target))


if __name__ == "__main__":
    main()
