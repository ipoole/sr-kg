#!/usr/bin/env python3
"""Upload exact site packages and request validation/deployment using authenticated gh."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from srkg.site_deployment import digest, read_package

REPO = 'ipoole/sr-kg'
SITE = 'https://physicskg.org/'
ASSET = 'site.tar.gz'
WORKFLOW = 'deploy-site.yml'


def gh(*args, **kwargs):
    return subprocess.check_output(['gh', *args], text=True, **kwargs).strip()


def live_manifest():
    request = Request(SITE + 'deployment.json', headers={'Cache-Control': 'no-cache'})
    try:
        with urlopen(request, timeout=30) as response:
            value = json.load(response)
    except HTTPError as error:
        if error.code == 404:
            return None
        raise
    if not re.fullmatch(r'site-[A-Za-z0-9._-]+', value.get('tag', '')):
        raise ValueError('Live site returned an invalid deployment identity')
    return value


def check_base(manifest, live, rollback=False):
    if not rollback and manifest['base'] != (live['tag'] if live else None):
        raise ValueError('Live deployment changed: prepare again from the current package')


def download(tag, directory):
    if not re.fullmatch(r'site-[A-Za-z0-9._-]+', tag):
        raise ValueError('Invalid deployment tag')
    gh('release', 'download', tag, '--repo', REPO, '--pattern', ASSET,
       '--pattern', 'site.sha256', '--dir', str(directory))
    checksum = (directory / 'site.sha256').read_text().strip()
    if not re.fullmatch('[0-9a-f]{64}', checksum):
        raise ValueError('Invalid recorded archive checksum')
    path = directory / ASSET
    _, manifest = read_package(path, checksum)
    if manifest['tag'] != tag:
        raise ValueError('Downloaded package has the wrong deployment tag')
    return path, checksum, manifest


def upload(path):
    _, manifest = read_package(path)
    checksum = digest(path.read_bytes())
    tag = manifest['tag']
    notes = (f"Source commit: {manifest['source_commit']}\n"
             f"Channel: {manifest['channel']}\nBase deployment: {manifest['base']}\n"
             f"SHA-256: {checksum}\n\nUpload alone does not publish this website.\n")
    with tempfile.TemporaryDirectory(prefix='physicskg-upload-') as temp:
        directory = Path(temp)
        archive = directory / ASSET
        archive.write_bytes(path.read_bytes())
        (directory / 'site.sha256').write_text(checksum + '\n')
        notes_path = directory / 'notes.md'
        notes_path.write_text(notes)
        # Existing tags/releases fail rather than silently replacing an archive.
        gh('release', 'create', tag, '--repo', REPO, '--target', manifest['source_commit'],
           '--title', f"Website package: {tag}", '--notes-file', str(notes_path),
           '--prerelease', '--latest=false', str(archive), str(directory / 'site.sha256'))
    return checksum, manifest


def dispatch(tag, checksum, deploy=False, rollback=False):
    if rollback and not deploy:
        raise ValueError('Rollback is meaningful only with --deploy')
    gh('workflow', 'run', WORKFLOW, '--repo', REPO, '--ref', 'main',
       '-f', f'tag={tag}', '-f', f'sha256={checksum}',
       '-f', f'deploy={str(deploy).lower()}', '-f', f'rollback={str(rollback).lower()}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    current = commands.add_parser('current', help='Fetch the currently deployed package as the update base')
    current.add_argument('--out', type=Path, default=Path('.deployment/current-site.tar.gz'))
    send = commands.add_parser('upload', help='Upload only; leaves the live site unchanged')
    send.add_argument('archive', type=Path)
    request = commands.add_parser('request', help='Validate by default; --deploy explicitly publishes on main')
    request.add_argument('--tag', required=True)
    request.add_argument('--sha256', required=True)
    request.add_argument('--deploy', action='store_true')
    request.add_argument('--rollback', action='store_true')
    check = commands.add_parser('check-live', help='Reject a stale package base')
    check.add_argument('archive', type=Path)
    check.add_argument('--sha256', required=True)
    check.add_argument('--rollback', action='store_true')
    args = parser.parse_args()
    if args.command == 'current':
        live = live_manifest()
        if live is None:
            parser.error('No artefact deployment exists yet; bootstrap explicitly for the cutover')
        with tempfile.TemporaryDirectory(prefix='physicskg-current-') as temp:
            path, checksum, _ = download(live['tag'], Path(temp))
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_bytes(path.read_bytes())
        print(json.dumps(dict(archive=str(args.out), sha256=checksum, tag=live['tag'])))
    elif args.command == 'upload':
        checksum, manifest = upload(args.archive)
        print(json.dumps(dict(tag=manifest['tag'], sha256=checksum, deployed=False)))
    elif args.command == 'request':
        if not re.fullmatch(r'site-[A-Za-z0-9._-]+', args.tag) or not re.fullmatch('[0-9a-f]{64}', args.sha256):
            parser.error('Invalid deployment tag or checksum')
        dispatch(args.tag, args.sha256, args.deploy, args.rollback)
        print('Deployment requested' if args.deploy else 'Validation requested; live website unchanged')
    else:
        _, manifest = read_package(args.archive, args.sha256)
        check_base(manifest, live_manifest(), args.rollback)
        print('Live deployment base verified' if not args.rollback else 'Explicit rollback: base check bypassed')


if __name__ == '__main__':
    main()
