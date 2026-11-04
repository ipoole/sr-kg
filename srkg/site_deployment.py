"""Package exact local builds; verify before any website deployment.

Standard library only: the Actions validator does not need the generator environment.
"""
from __future__ import annotations

import gzip
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
from urllib.parse import unquote, urlsplit

SCHEMA = 1
MAX_SIZE = 1024 ** 3
SITE_FILES = (
    'index.html', 'privacy.html', 'terms.html', 'site.css', 'favicon.svg',
    'favicon-32.png', 'favicon.ico', 'apple-touch-icon.png',
    'physicskg-logo-120.png', 'robots.txt', 'sitemap.xml', 'CNAME',
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(name: str) -> str:
    path = PurePosixPath(name)
    if not name or name.startswith('/') or '\\' in name or any(
        part in ('', '.', '..') for part in name.split('/')
    ) or str(path) != name:
        raise ValueError(f'Unsafe package path: {name!r}')
    return name


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and attrs.get('rel') == 'canonical':
            return
        for attr in ('href', 'src'):
            if attr in attrs:
                self.links.append(attrs[attr])


def validate_site(files: dict[str, bytes]) -> None:
    required = {*SITE_FILES, 'output/PhysicsKG.html',
                'output/interactive_graph.html', 'output/lib/bindings/utils.js'}
    missing = required - files.keys()
    if missing:
        raise ValueError(f'Missing site files: {sorted(missing)}')
    if files['CNAME'].strip() != b'physicskg.org':
        raise ValueError('Unexpected custom domain')
    if 'preview/PhysicsKG.html' in files and 'preview/lib/bindings/utils.js' not in files:
        raise ValueError('Preview library is missing')
    if sum(map(len, files.values())) > MAX_SIZE:
        raise ValueError('Site exceeds the Pages 1 GiB limit')
    for name, data in files.items():
        safe_path(name)
        if not name.endswith('.html'):
            continue
        parser = LocalLinks()
        parser.feed(data.decode('utf-8'))
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            # Normalise URL paths, permitting ordinary ../ navigation within the site.
            parts = [] if url.path.startswith('/') else list(PurePosixPath(name).parent.parts)
            for part in unquote(url.path).split('/'):
                if part == '..':
                    if not parts:
                        raise ValueError(f'Link escapes site: {name}: {link}')
                    parts.pop()
                elif part not in ('', '.'):
                    parts.append(part)
            target = '/'.join(parts)
            if url.path.endswith('/') or not target:
                target = (target + '/' if target else '') + 'index.html'
            if target not in files:
                raise ValueError(f'Broken local link: {name}: {link}')


def assemble(root: Path, viewer: Path, channel: str, previous=None) -> dict[str, bytes]:
    if channel not in ('release', 'preview'):
        raise ValueError('Channel must be release or preview')
    if channel == 'preview' and previous is None:
        raise ValueError('Preview requires a previous complete site package')
    files = dict(previous or {})
    files.pop('deployment.json', None)
    if channel == 'release':
        # New release owns all root files; preserve only the independently updated preview.
        files = {k: v for k, v in files.items() if k.startswith('preview/')}
        files.update({name: (root / 'website' / name).read_bytes() for name in SITE_FILES})
        files['output/interactive_graph.html'] = (root / 'output/interactive_graph.html').read_bytes()
        directory = 'output'
    else:
        files = {k: v for k, v in files.items() if not k.startswith('preview/')}
        directory = 'preview'
    files[f'{directory}/PhysicsKG.html'] = viewer.read_bytes()
    for path in sorted((root / 'lib').rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Library symlink is not allowed: {path}')
        if path.is_file():
            files[f'{directory}/lib/{path.relative_to(root / "lib").as_posix()}'] = path.read_bytes()
    validate_site(files)
    return files


def make_package(files, destination: Path, *, tag: str, source_commit: str,
                 channel: str, base: str | None):
    if not re.fullmatch(r'site-[A-Za-z0-9._-]+', tag):
        raise ValueError('Deployment tag must start site- and contain safe characters')
    if not re.fullmatch(r'[0-9a-f]{40}', source_commit):
        raise ValueError('Source commit must be a full Git SHA')
    validate_site(files)
    files = dict(files)
    files.pop('deployment.json', None)
    manifest = dict(schema=SCHEMA, tag=tag, source_commit=source_commit,
                    channel=channel, base=base,
                    files={name: digest(data) for name, data in sorted(files.items())})
    files['deployment.json'] = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w') as archive:
                for name, data in sorted(files.items()):
                    safe_path(name)
                    entry = tarfile.TarInfo(name)
                    entry.size = len(data)
                    entry.mode = 0o644
                    entry.mtime = 0
                    archive.addfile(entry, io.BytesIO(data))
    return digest(destination.read_bytes()), manifest


def read_package(path: Path, expected_sha256: str | None = None):
    if expected_sha256 and digest(path.read_bytes()) != expected_sha256:
        raise ValueError('Archive checksum mismatch')
    files = {}
    size = 0
    with tarfile.open(path, 'r:gz') as archive:
        for entry in archive:
            safe_path(entry.name)
            if not entry.isfile() or entry.name in files:
                raise ValueError(f'Non-regular or duplicate archive member: {entry.name}')
            size += entry.size
            if size > MAX_SIZE:
                raise ValueError('Archive exceeds the Pages 1 GiB limit')
            files[entry.name] = archive.extractfile(entry).read()
    manifest = json.loads(files.pop('deployment.json'))
    if manifest.get('schema') != SCHEMA:
        raise ValueError('Unsupported deployment schema')
    if manifest.get('channel') not in ('release', 'preview') or not re.fullmatch(
        r'site-[A-Za-z0-9._-]+', manifest.get('tag', '')
    ) or not re.fullmatch(r'[0-9a-f]{40}', manifest.get('source_commit', '')):
        raise ValueError('Invalid deployment identity')
    actual = {name: digest(data) for name, data in files.items()}
    if actual != manifest.get('files'):
        raise ValueError('Site file checksums do not match manifest')
    validate_site(files)
    return files, manifest


def extract_verified(path: Path, destination: Path, sha256: str):
    files, manifest = read_package(path, sha256)
    if destination.exists():
        raise ValueError('Extraction destination must not already exist')
    destination.mkdir(parents=True)
    for name, data in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    (destination / 'deployment.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
    return manifest
