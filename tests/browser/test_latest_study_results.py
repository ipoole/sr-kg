"""Study persistence keeps outcomes, not submission histories or attempt counts."""
import pytest


@pytest.mark.browser
def test_repeated_answers_replace_result_and_survive_reload(browser_graph):
    page = browser_graph.page
    page.evaluate("""()=>{
      kgStudyProgress.recordAttempt('2.1.q1','incorrect','2026-11-01T10:00:00Z');
      kgStudyProgress.recordAttempt('2.1.q1','unknown','2026-11-01T10:01:00Z');
      kgStudyProgress.recordAttempt('2.1.q1','correct','2026-11-01T10:02:00Z');
    }""")
    profile = page.evaluate('kgPersonalData.getSnapshot()')
    assert 'studyAttempts' not in profile
    assert set(profile['studyResults']) == {'2.1.q1'}
    assert profile['studyResults']['2.1.q1']['outcome'] == 'correct'
    assert 'attemptCount' not in profile['studyResults']['2.1.q1']
    page.reload(wait_until='load')
    assert page.evaluate("kgStudyProgress.getQuestion('2.1.q1').lastOutcome") == 'correct'
    browser_graph.open_control_section('kg_study_section')
    assert 'attempt' not in page.locator('#kg_study_list').inner_text().lower()


@pytest.mark.browser
def test_legacy_history_compacts_and_stale_sync_cannot_revive_reset(browser_graph):
    page = browser_graph.page
    result = page.evaluate("""()=>{
      const legacy=kgPersonalData.getSnapshot(); legacy.schemaVersion=1; delete legacy.studyResults;
      legacy.studyAttempts=[
        {id:'a',questionId:'2.1.q1',outcome:'incorrect',attemptedAt:'2026-11-01T10:00:00Z',deviceId:'a',attemptCount:20},
        {id:'b',questionId:'2.1.q1',outcome:'correct',attemptedAt:'2026-11-01T10:02:00Z',deviceId:'b',attemptCount:1},
        {id:'c',questionId:'unloaded.q1',outcome:'correct',attemptedAt:'2026-11-01T10:03:00Z',deviceId:'a',attemptCount:5}
      ];
      kgPersonalData.replaceSnapshot(legacy);
      const migrated=kgPersonalData.getSnapshot();
      kgPersonalData.resetStudy('2.1.q1');
      kgPersonalData.mergeSnapshot(legacy);
      return {migrated, merged:kgPersonalData.getSnapshot(),state:kgPersonalData.getStudyState()};
    }""")
    assert result['migrated']['schemaVersion'] == 2
    assert len(result['migrated']['studyResults']) == 2
    assert result['migrated']['studyResults']['2.1.q1']['outcome'] == 'correct'
    assert '2.1.q1' not in result['state']['questions']
    assert result['merged']['studyResults']['unloaded.q1']['outcome'] == 'correct'
    assert 'studyAttempts' not in result['merged']


@pytest.mark.browser
def test_results_merge_deterministically_and_archive_round_trip(browser_graph):
    page = browser_graph.page
    result = page.evaluate("""()=>{
      const a=kgPersonalData.getSnapshot(), b=kgPersonalData.getSnapshot();
      a.studyResults={'2.1.q1':{questionId:'2.1.q1',outcome:'correct',updatedAt:'2026-11-01T10:00:00Z',deviceId:'a'}};
      b.studyResults={'2.1.q1':{questionId:'2.1.q1',outcome:'incorrect',updatedAt:'2026-11-01T10:00:00Z',deviceId:'b'}};
      kgPersonalData.replaceSnapshot(a); kgPersonalData.mergeSnapshot(b);
      const ab=kgPersonalData.getSnapshot().studyResults;
      kgPersonalData.replaceSnapshot(b); kgPersonalData.mergeSnapshot(a);
      const ba=kgPersonalData.getSnapshot().studyResults;
      const restored=kgPersonalDataArchive.importBytes(kgPersonalDataArchive.exportBytes(kgPersonalData.getSnapshot()));
      return {ab,ba,restored:restored.studyResults};
    }""")
    assert result['ab'] == result['ba'] == result['restored']


@pytest.mark.browser
def test_browser_profile_upgrades_in_place_and_keeps_other_collections(browser_graph):
    page = browser_graph.page
    before = page.evaluate("""()=>{
      kgContentReadProgress.setRead('2.2.definition',true);
      const legacy=kgPersonalData.getSnapshot(); legacy.schemaVersion=1; delete legacy.studyResults;
      legacy.studyAttempts=[{id:'old',questionId:'2.1.q1',outcome:'correct',attemptedAt:'2026-11-01T10:00:00Z',attemptCount:7}];
      localStorage.setItem('srkg.personalData.v1',JSON.stringify(legacy));
      localStorage.setItem('srkg.studyProgress.v1', JSON.stringify({version:1,questions:{'2.1.q1':{attemptCount:7,lastOutcome:'correct',lastAttemptAt:'2026-11-01T10:00:00Z'}}}));
      return legacy;
    }""")
    page.reload(wait_until='load')
    after = page.evaluate('kgPersonalData.getSnapshot()')
    assert after['schemaVersion'] == 2
    assert after['studyResults']['2.1.q1']['outcome'] == 'correct'
    for key in ['profileId','createdAt','notes','layout','readingProgress']:
        assert after[key] == before[key]
    assert page.evaluate("JSON.parse(localStorage.getItem('srkg.personalData.v1')).studyResultsVersion") == 2
    assert 'attemptCount' not in page.evaluate("JSON.parse(localStorage.getItem('srkg.studyProgress.v1')).questions['2.1.q1']")


@pytest.mark.browser
def test_old_csv_archive_keeps_latest_result_and_discards_counts(browser_graph):
    import io
    import zipfile

    page = browser_graph.page
    raw = bytes(page.evaluate('Array.from(kgPersonalDataArchive.exportBytes(kgPersonalData.getSnapshot()))'))
    old = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as current, zipfile.ZipFile(old, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name in current.namelist():
            if name in ['study_results.csv', 'study_attempts.csv']:
                continue
            body = current.read(name)
            if name == 'manifest.csv':
                body = body.replace(b'schema_version,2', b'schema_version,1')
            archive.writestr(name, body)
        archive.writestr('study_attempts.csv', 'attempt_id,question_id,outcome,attempted_at,device_id,attempt_count\n'
            'one,2.1.q1,incorrect,2026-11-01T10:00:00Z,a,9\n'
            'two,2.1.q1,correct,2026-11-01T10:01:00Z,b,1\n')
    restored = page.evaluate('bytes=>kgPersonalDataArchive.importBytes(new Uint8Array(bytes))', list(old.getvalue()))
    assert restored['schemaVersion'] == 2
    assert restored['studyResults']['2.1.q1']['outcome'] == 'correct'
    assert 'attemptCount' not in restored['studyResults']['2.1.q1']
    assert 'studyAttempts' not in restored


@pytest.mark.browser
def test_answer_immediately_after_reset_is_not_lost_to_timestamp_tie(browser_graph):
    from datetime import datetime, timezone

    page = browser_graph.page
    page.clock.set_fixed_time(datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc))
    page.evaluate("""()=>{
      kgStudyProgress.recordAttempt('2.1.q1','incorrect');
      kgStudyProgress.recordAttempt('2.1.q1','correct');
      if (kgStudyProgress.getQuestion('2.1.q1').lastOutcome !== 'correct') { throw new Error('Same-tick answer lost'); }
      kgStudyProgress.resetQuestion('2.1.q1');
      kgStudyProgress.recordAttempt('2.1.q1','correct');
    }""")
    assert page.evaluate("kgStudyProgress.getQuestion('2.1.q1').lastOutcome") == 'correct'


@pytest.mark.browser
def test_shared_storage_envelope_remains_compatible_with_published_viewer(browser_graph):
    page = browser_graph.page
    wire = page.evaluate("""()=>{
      kgStudyProgress.recordAttempt('2.1.q1','incorrect','2026-11-01T10:00:00Z');
      kgStudyProgress.recordAttempt('2.1.q1','correct','2026-11-01T10:01:00Z');
      return JSON.parse(localStorage.getItem('srkg.personalData.v1'));
    }""")
    assert wire['schemaVersion'] == 1
    assert wire['studyResultsVersion'] == 2
    assert len(wire['studyAttempts']) == 1
    assert wire['studyAttempts'][0]['attemptCount'] == 1  # Single retained result, not a total.
    assert wire['studyAttempts'][0]['outcome'] == 'correct'
    # An older viewer strips unknown fields and appends a new answer.
    wire.pop('studyResultsVersion')
    wire['studyAttempts'].append({'id':'older-viewer-write','questionId':'2.1.q1',
        'outcome':'incorrect','attemptedAt':'2026-11-02T10:00:00Z','deviceId':'old','attemptCount':1})
    page.evaluate("value=>localStorage.setItem('srkg.personalData.v1',JSON.stringify(value))", wire)
    page.reload(wait_until='load')
    assert page.evaluate("kgStudyProgress.getQuestion('2.1.q1').lastOutcome") == 'incorrect'
    assert len(page.evaluate("JSON.parse(localStorage.getItem('srkg.personalData.v1')).studyAttempts")) == 1
