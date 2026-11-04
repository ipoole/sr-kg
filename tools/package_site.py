#!/usr/bin/env python3
"""Create or validate an exact-build site archive; no network or generator invocation."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from srkg.site_deployment import assemble, extract_verified, make_package, read_package

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    package = commands.add_parser('package')
    package.add_argument('--viewer', type=Path, default=ROOT / 'output/PhysicsKG.html')
    package.add_argument('--channel', choices=['release', 'preview'], default='release')
    package.add_argument('--previous', type=Path)
    package.add_argument('--bootstrap', action='store_true')
    package.add_argument('--tag')
    package.add_argument('--out', type=Path, default=ROOT / '.deployment/site.tar.gz')
    verify = commands.add_parser('verify')
    verify.add_argument('archive', type=Path)
    verify.add_argument('--sha256', required=True)
    verify.add_argument('--extract', type=Path)
    args = parser.parse_args()
    if args.command == 'verify':
        if args.extract:
            manifest = extract_verified(args.archive, args.extract, args.sha256)
        else:
            _, manifest = read_package(args.archive, args.sha256)
        print(json.dumps(manifest, indent=2))
        return
    if bool(args.previous) == args.bootstrap:
        parser.error('Choose exactly one of --previous or --bootstrap')
    previous, base = None, None
    if args.previous:
        previous, manifest = read_package(args.previous)
        base = manifest['tag']
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    # Do not label uncommitted source as a reproducible source commit. Generated
    # viewers are ignored build products, so do not appear in this tracked diff.
    dirty = subprocess.check_output(['git', 'diff', 'HEAD', '--name-only'], cwd=ROOT, text=True).splitlines()
    if dirty:
        parser.error('Commit source changes before packaging: ' + ', '.join(dirty))
    tag = args.tag or f'site-{datetime.now(timezone.utc):%Y%m%dT%H%M%S%fZ}-{commit[:8]}'
    files = assemble(ROOT, args.viewer, args.channel, previous)
    checksum, manifest = make_package(files, args.out, tag=tag, source_commit=commit,
                                      channel=args.channel, base=base)
    print(json.dumps(dict(archive=str(args.out.resolve()), sha256=checksum,
                          tag=tag, source_commit=commit, channel=args.channel,
                          base=base, files=len(manifest['files'])), indent=2))


if __name__ == '__main__':
    main()
