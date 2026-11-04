import importlib.util
from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml

from srkg.site_deployment import assemble, make_package

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('publish_site', ROOT / 'tools/publish_site.py')
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)


def test_stale_update_cannot_overwrite_newer_deployment():
    manifest = {'base': 'site-a'}
    publish.check_base(manifest, {'tag': 'site-a'})
    with pytest.raises(ValueError, match='Live deployment changed'):
        publish.check_base(manifest, {'tag': 'site-b'})
    publish.check_base(manifest, {'tag': 'site-b'}, rollback=True)
    publish.check_base({'base': None}, None)
    with pytest.raises(ValueError, match='Live deployment changed'):
        publish.check_base({'base': None}, {'tag': 'site-b'})


def test_request_validates_by_default_and_deploys_only_explicitly(monkeypatch):
    gh = Mock(return_value='')
    monkeypatch.setattr(publish, 'gh', gh)
    publish.dispatch('site-test', 'a' * 64)
    args = gh.call_args.args
    assert 'deploy=false' in args
    assert 'rollback=false' in args
    assert args[args.index('--ref') + 1] == 'main'
    publish.dispatch('site-test', 'a' * 64, deploy=True, rollback=True)
    assert 'deploy=true' in gh.call_args.args
    assert 'rollback=true' in gh.call_args.args
    gh.reset_mock()
    with pytest.raises(ValueError, match='only with --deploy'):
        publish.dispatch('site-test', 'a' * 64, rollback=True)
    gh.assert_not_called()


def test_upload_pins_source_and_does_not_dispatch_or_overwrite(monkeypatch, tmp_path):
    # Use the real website files and a minimal viewer, without invoking the generator.
    viewer = tmp_path / 'viewer.html'
    viewer.write_text('<html>tested exact bytes</html>')
    archive = tmp_path / 'candidate.tar.gz'
    checksum, _ = make_package(assemble(ROOT, viewer, 'release'), archive,
                              tag='site-upload-test', source_commit='b' * 40,
                              channel='release', base=None)
    calls = []

    def gh(*args):
        calls.append(args)
        asset = Path(args[-2])
        assert asset.name == 'site.tar.gz'
        assert asset.read_bytes() == archive.read_bytes()
        assert Path(args[-1]).read_text().strip() == checksum
        notes = Path(args[args.index('--notes-file') + 1]).read_text()
        assert checksum in notes and 'b' * 40 in notes
        return ''

    monkeypatch.setattr(publish, 'gh', gh)
    actual, manifest = publish.upload(archive)
    assert actual == checksum and manifest['tag'] == 'site-upload-test'
    assert len(calls) == 1
    assert calls[0][:3] == ('release', 'create', 'site-upload-test')
    assert '--prerelease' in calls[0]
    assert calls[0][calls[0].index('--target') + 1] == 'b' * 40
    assert '--clobber' not in calls[0]


def test_workflow_readonly_validation_and_main_only_explicit_deployment():
    workflow = yaml.load((ROOT / '.github/workflows/deploy-site.yml').read_text(), Loader=yaml.BaseLoader)
    assert workflow['permissions'] == {'contents': 'read'}
    assert workflow['on']['workflow_dispatch']['inputs']['deploy']['default'] == 'false'
    assert workflow['concurrency']['cancel-in-progress'] == 'false'
    validate = workflow['jobs']['validate']
    deploy = workflow['jobs']['deploy']
    assert "inputs.deploy" in deploy['if'] and "refs/heads/main" in deploy['if']
    assert "workflow_dispatch" in deploy['if']
    assert deploy['needs'] == 'validate'
    assert deploy['permissions'] == {'contents': 'read', 'pages': 'write', 'id-token': 'write'}
    assert not any('deploy-pages@' in step.get('uses', '') for step in validate['steps'])
    assert any('check-live' in step.get('run', '') for step in deploy['steps'])
    assert not any('generate_pyvis' in step.get('run', '') for job in workflow['jobs'].values()
                   for step in job['steps'])


def test_deployment_waits_for_visible_manifest_before_unlocking(monkeypatch):
    expected = {'tag': 'site-new', 'files': {'index.html': 'new-hash'}}
    live = Mock(side_effect=[{'tag': 'site-old'}, expected])
    sleep = Mock()
    monkeypatch.setattr(publish, 'live_manifest', live)
    monkeypatch.setattr(publish.time, 'sleep', sleep)
    publish.wait_live(expected, attempts=2)
    assert live.call_count == 2
    sleep.assert_called_once_with(3)
    monkeypatch.setattr(publish, 'live_manifest', lambda: {'tag': 'site-old'})
    with pytest.raises(ValueError, match='inspect before retrying'):
        publish.wait_live(expected, attempts=1)
