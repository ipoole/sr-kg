"""Deployment invariants: exact bytes, channel isolation, integrity and extraction safety."""
import io
import json
from pathlib import Path
import tarfile

import pytest

from srkg.site_deployment import (
    GUIDE_FILES, SITE_FILES, assemble, digest, extract_verified, make_package, read_package, safe_path,
    validate_site,
)

ROOT = Path(__file__).resolve().parents[1]
SHA = 'a' * 40


@pytest.fixture
def source(tmp_path):
    root = tmp_path / 'repo'
    (root / 'website').mkdir(parents=True)
    for name in SITE_FILES:
        (root / 'website' / name).parent.mkdir(parents=True, exist_ok=True)
        (root / 'website' / name).write_bytes((ROOT / 'website' / name).read_bytes())
    (root / 'output').mkdir()
    (root / 'output/interactive_graph.html').write_bytes((ROOT / 'output/interactive_graph.html').read_bytes())
    (root / 'lib/bindings').mkdir(parents=True)
    (root / 'lib/bindings/utils.js').write_bytes(b'// exact library bytes\n')
    viewer = root / 'output/PhysicsKG.html'
    viewer.write_bytes(b'<html><script src="lib/bindings/utils.js"></script><a href="/privacy.html">Privacy</a></html>')
    return root, viewer


def package(tmp_path, files, tag='site-test', channel='release', base=None):
    path = tmp_path / f'{tag}.tar.gz'
    checksum, _ = make_package(files, path, tag=tag, source_commit=SHA, channel=channel, base=base)
    return path, checksum


def test_packaging_preserves_bytes_and_is_reproducible(source, tmp_path):
    root, viewer = source
    files = assemble(root, viewer, 'release')
    first, checksum = package(tmp_path, files)
    second, again = package(tmp_path, files, tag='site-test')
    assert checksum == again
    actual, manifest = read_package(first, checksum)
    assert actual['output/PhysicsKG.html'] == viewer.read_bytes()
    assert actual['user-guide.html'] == (root / 'website/user-guide.html').read_bytes()
    for screenshot in (root / 'website/guide').glob('*.png'):
        assert actual[f'guide/{screenshot.name}'] == screenshot.read_bytes()
    assert actual['output/lib/bindings/utils.js'] == (root / 'lib/bindings/utils.js').read_bytes()
    assert manifest['source_commit'] == SHA
    assert manifest['files']['output/PhysicsKG.html'] == digest(viewer.read_bytes())
    assert checksum == digest(second.read_bytes())
    destination = tmp_path / 'extracted'
    extract_verified(first, destination, checksum)
    assert (destination / 'output/PhysicsKG.html').read_bytes() == viewer.read_bytes()
    assert json.loads((destination / 'deployment.json').read_text()) == manifest
    with pytest.raises(ValueError, match='already exist'):
        extract_verified(first, destination, checksum)


def test_alternating_release_and_preview_updates_preserve_other_channel(source, tmp_path):
    root, viewer = source
    original = assemble(root, viewer, 'release')
    viewer.write_bytes(b'<html>experimental preview</html>')
    preview = assemble(root, viewer, 'preview', original)
    assert {k: v for k, v in preview.items() if not k.startswith('preview/')} == original
    path, checksum = package(tmp_path, preview, channel='preview', base='site-original')
    restored, manifest = read_package(path, checksum)
    assert manifest['base'] == 'site-original'
    viewer.write_bytes(b'<html>new release</html>')
    release = assemble(root, viewer, 'release', restored)
    assert release['output/PhysicsKG.html'] == viewer.read_bytes()
    assert {k: v for k, v in release.items() if k.startswith('preview/')} == {
        k: v for k, v in preview.items() if k.startswith('preview/')
    }


def test_preview_cannot_accidentally_bootstrap_empty_release(source):
    with pytest.raises(ValueError, match='previous'):
        assemble(*source, 'preview')


def test_guide_preview_preserves_a_release_without_the_guide(source, tmp_path):
    root, viewer = source
    previous = assemble(root, viewer, 'release')
    for name in GUIDE_FILES:
        previous.pop(name)
    previous['index.html'] = b'<html>Earlier public homepage</html>'
    # Existing deployment archives remain readable as website features grow.
    path, checksum = package(tmp_path, previous)
    previous, _ = read_package(path, checksum)
    preview = assemble(root, viewer, 'preview', previous)
    assert {k: v for k, v in preview.items() if not k.startswith('preview/')} == previous
    for name in (*GUIDE_FILES, 'site.css', 'physicskg-logo-120.png'):
        assert preview[f'preview/{name}'] == (root / 'website' / name).read_bytes()


def test_guide_preview_requires_its_images(source):
    previous = assemble(*source, 'release')
    preview = assemble(*source, 'preview', previous)
    preview.pop('preview/guide/phone-both.png')
    with pytest.raises(ValueError, match='Broken local link'):
        validate_site(preview)


def test_broken_local_dependencies_fail_packaging(source):
    root, viewer = source
    viewer.write_text('<script src="lib/missing.js"></script>')
    with pytest.raises(ValueError, match='Broken local link'):
        assemble(root, viewer, 'release')


def test_invalid_checksum_or_changed_file_is_rejected(source, tmp_path):
    path, checksum = package(tmp_path, assemble(*source, 'release'))
    with pytest.raises(ValueError, match='Archive checksum'):
        read_package(path, '0' * 64)
    # Corrupt a member while preserving the manifest, simulating a repacked upload.
    with tarfile.open(path, 'r:gz') as archive:
        members = {entry.name: archive.extractfile(entry).read() for entry in archive}
    members['privacy.html'] = b'changed'
    with tarfile.open(path, 'w:gz') as archive:
        for name, data in members.items():
            entry = tarfile.TarInfo(name)
            entry.size = len(data)
            archive.addfile(entry, io.BytesIO(data))
    with pytest.raises(ValueError, match='file checksums'):
        read_package(path)


@pytest.mark.parametrize('name', ['../escape', '/absolute', 'a/../b', 'a//b', './a', 'a\\b'])
def test_unsafe_paths_rejected(name):
    with pytest.raises(ValueError, match='Unsafe'):
        safe_path(name)


@pytest.mark.parametrize('kind', ['symlink', 'duplicate'])
def test_unsafe_archive_members_rejected(tmp_path, kind):
    path = tmp_path / 'bad.tar.gz'
    with tarfile.open(path, 'w:gz') as archive:
        entry = tarfile.TarInfo('file')
        if kind == 'symlink':
            entry.type = tarfile.SYMTYPE
            entry.linkname = '/etc/passwd'
            archive.addfile(entry)
        else:
            archive.addfile(entry, io.BytesIO(b''))
            archive.addfile(entry, io.BytesIO(b''))
    with pytest.raises(ValueError, match='Non-regular or duplicate'):
        read_package(path)
