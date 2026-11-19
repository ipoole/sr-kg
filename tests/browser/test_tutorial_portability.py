"""Tutorial definitions, independent storage and conflict-safe cloud merge."""
import pytest
from test_personal_tutorials import tutorial_graph, _library


@pytest.mark.browser
def test_tutorial_json_zip_and_library_round_trip(tutorial_graph):
    page = _library(tutorial_graph)
    result = page.evaluate('''async()=>{
      const p=kgTutorialPortable,store=kgPersonalData.tutorials;
      const original=await store.create(tutorialData[0],{tutorialId:tutorialData[0].tutorial_id,version:'5.0.1'});
      const json=p.importSingle(p.exportSingle(original,true));
      const zip=p.importSingle(p.exportSingle(original,false));
      const files=kgTextZip.decode(p.exportSingle(original,false));
      const records=p.importCollection(p.exportCollection([original]));
      const unavailable=JSON.parse(JSON.stringify(original));
      unavailable.route.steps[0].action={command:'select',target:'concept:missing.example'};
      unavailable.route.steps[0].pointer={target:'graph:concept:missing.example'};
      const retained=p.importSingle(p.exportSingle(unavailable,true));
      return {original,json,zip,files:Object.keys(files).sort(),records,retained};
    }''')
    assert result['json'] == result['zip'] == result['original']
    assert result['records'] == [result['original']]
    assert result['files'] == ['manifest.json','tutorial.json']
    assert result['retained']['route']['steps'][0]['action']['target'] == 'concept:missing.example'


@pytest.mark.browser
def test_tutorial_malformed_imports_and_corrupt_zip_do_not_change_storage(tutorial_graph):
    page = _library(tutorial_graph)
    result = page.evaluate('''async()=>{
      const p=kgTutorialPortable,store=kgPersonalData.tutorials,record=await store.create(tutorialData[0]);
      const before=await store.snapshot(),errors=[];
      const definition=JSON.parse(new TextDecoder().decode(p.exportSingle(record,true)));
      definition.tutorial.route.steps[0].action={command:'run-script',code:'alert(1)'};
      try{p.importSingle(new TextEncoder().encode(JSON.stringify(definition)));}catch(e){errors.push(e.message);}
      const zip=p.exportSingle(record,false);zip[50]^=1;
      try{p.importSingle(zip);}catch(e){errors.push(e.message);}
      const unsafe=kgTextZip.encode({'../tutorial.json':'{}'});
      try{p.importSingle(unsafe);}catch(e){errors.push(e.message);}
      return {errors,before,after:await store.snapshot()};
    }''')
    assert len(result['errors']) == 3
    assert result['after'] == result['before']


@pytest.mark.browser
def test_tutorial_database_upgrade_preserves_v1_and_snapshot_cas(tutorial_graph):
    page = _library(tutorial_graph)
    result = page.evaluate('''async()=>{
      const record=await kgPersonalData.tutorials.create(tutorialData[0]),name='tutorial-upgrade';
      await new Promise((resolve,reject)=>{
        const r=indexedDB.open(name,1);r.onupgradeneeded=()=>r.result.createObjectStore('tutorials',{keyPath:'id'});
        r.onsuccess=()=>{const db=r.result,tx=db.transaction('tutorials','readwrite');tx.objectStore('tutorials').put(record);tx.oncomplete=()=>{db.close();resolve();};};r.onerror=()=>reject(r.error);
      });
      const store=kgCreateTutorialStore({databaseName:name}),before=await store.snapshot();
      record.route.title='Newer local edit';const newer=await store.save(record);
      let conflict=false;
      try{await store.commitSnapshot(before.records,{},before.records);}catch(e){conflict=e.code==='conflict';}
      return {before,newer,conflict,after:await store.snapshot()};
    }''')
    assert result['before']['records'][0]['route']['steps'] == result['newer']['route']['steps']
    assert result['conflict']
    assert result['after']['records'] == [result['newer']]


@pytest.mark.browser
def test_tutorial_merge_preserves_conflicts_and_deletion_without_duplicate_copies(tutorial_graph):
    page = _library(tutorial_graph)
    result = page.evaluate('''async()=>{
      const p=kgTutorialPortable,store=kgPersonalData.tutorials,sync=kgCreateTutorialSync({portable:p});
      const base=await store.create(tutorialData[0]),baseline=await sync.stamps([base]);
      const a=JSON.parse(JSON.stringify(base)),b=JSON.parse(JSON.stringify(base));
      a.route.title='Laptop edit';a.revisionId='revision:laptop';
      b.route.title='Phone edit';b.revisionId='revision:phone';
      const merged=await sync.merge([a],[b],baseline),reverse=await sync.merge([b],[a],baseline);
      const again=await sync.merge(merged.records,[b],await sync.stamps(merged.records));
      const deleted=JSON.parse(JSON.stringify(b));deleted.deletedAt='2026-11-17T12:00:00.000Z';deleted.revisionId='revision:deleted';
      const deletion=await sync.merge([a],[deleted],baseline);
      return {merged,reverse,again,deletion,id:base.id};
    }''')
    merged = result['merged']['records']
    assert len(merged) == 2
    assert {r['route']['title'] for r in merged} == {'Laptop edit','Phone edit'}
    assert result['reverse']['records'] == merged
    assert result['again']['records'] == merged
    deleted = next(r for r in result['deletion']['records'] if r['id']==result['id'])
    assert deleted['deletedAt']
    assert any(r['conflictOf']==result['id'] and r['route']['title']=='Laptop edit'
               for r in result['deletion']['records'] if not r['deletedAt'])


@pytest.mark.browser
def test_tutorial_sync_retries_local_edits_during_upload_and_skips_unchanged_write(tutorial_graph):
    page = _library(tutorial_graph)
    result = page.evaluate('''async()=>{
      const p=kgTutorialPortable,store=kgPersonalData.tutorials,record=await store.create(tutorialData[0]);
      let remote=null,writes=0;
      const provider={read:async()=>remote,write:async bytes=>{
        writes++;remote={bytes,revision:'v'+writes};
        if(writes===1){const latest=await store.get(record.id);latest.route.title='Typed during upload';await store.save(latest);}
        return {revision:remote.revision};
      }};
      const before=kgPersonalData.getSnapshot();
      const sync=kgCreateTutorialSync({portable:p,store,provider});
      await sync.synchronize();const first=writes;await sync.synchronize();
      return {first,writes,local:(await store.snapshot()).records,remote:p.importCollection(remote.bytes),before,after:kgPersonalData.getSnapshot()};
    }''')
    assert result['first'] == result['writes'] == 2
    assert result['local'] == result['remote']
    assert any(r['route']['title']=='Typed during upload' for r in result['remote'])
    assert result['before'] == result['after']


@pytest.mark.browser
def test_tutorial_export_import_ui_makes_independent_copy_and_retains_unsaved_text(tutorial_graph):
    import json
    from test_personal_tutorials import _fill_draft
    from playwright.sync_api import expect
    page = _library(tutorial_graph)
    page.locator('#kg_tutorial_new').click()
    _fill_draft(page)
    original_id = page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    with page.expect_download() as captured:
        page.locator('#kg_tutorial_editor_advanced').evaluate('e=>e.open=true')
        page.locator('#kg_tutorial_editor_export').click()
    path = captured.value.path()
    page.keyboard.press('Escape')
    page.locator('#kg_tutorial_import_file').set_input_files(path)
    page.locator('#kg_tutorial_import_apply').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')
    imported_id = page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    assert imported_id != original_id
    assert page.locator('#kg_tutorial_editor_commentary').input_value() == r'Read this result: \(x^2=1\).'
    page.evaluate("()=>{kgPersonalData.tutorials.save=()=>Promise.reject(new Error('Storage full'));}")
    page.locator('#kg_tutorial_editor_title').fill('My unsaved title')
    expect(page.locator('#kg_tutorial_editor_status')).to_have_attribute('data-state','error')
    with page.expect_download() as captured:
        page.locator('#kg_tutorial_editor_advanced').evaluate('e=>e.open=true')
        page.locator('#kg_tutorial_editor_json').click()
    from pathlib import Path
    exported = json.loads(Path(captured.value.path()).read_text())
    assert exported['tutorial']['route']['title'] == 'My unsaved title'
    assert page.evaluate('(id)=>kgPersonalData.tutorials.get(id)',imported_id)['route']['title'] != 'My unsaved title'
    assert page.locator('#kg_tutorial_editor_retry').is_visible()


@pytest.mark.browser
def test_imported_missing_targets_can_be_repaired_in_editor(tutorial_graph):
    from playwright.sync_api import expect
    page = _library(tutorial_graph)
    payload = bytes(page.evaluate('''async()=>{
      const record=await kgPersonalData.tutorials.create(tutorialData[0]);record.route.domains=['missing'];
      record.route.steps[0].action.target='concept:missing.example';record.route.steps[0].pointer.target='graph:concept:missing.example';
      return Array.from(kgTutorialPortable.exportSingle(record,true));
    }'''))
    page.locator('#kg_tutorial_import_file').set_input_files({'name':'missing.json','mimeType':'application/json','buffer':payload})
    page.locator('#kg_tutorial_import_apply').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')
    assert page.locator('#kg_tutorial_editor_from').is_disabled()
    page.locator('#kg_tutorial_editor_advanced').evaluate('e=>e.open=true')
    page.locator('#kg_tutorial_editor_domains').fill('')
    page.locator('#kg_tutorial_editor_actions [data-field="target"]').select_option('concept:2.1')
    expect(page.locator('#kg_tutorial_editor_from')).to_be_enabled()


@pytest.mark.browser
@pytest.mark.parametrize("local_edit", [False, True])
def test_tutorial_sync_preserves_open_editor_text_focus_and_selection(tutorial_graph, local_edit):
    from test_personal_tutorials import _fill_draft, _record
    from playwright.sync_api import expect
    page = _library(tutorial_graph)
    page.locator('#kg_tutorial_new').click()
    _fill_draft(page)
    tutorial_id = page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    page.evaluate('''async id=>{
      const store=kgPersonalData.tutorials,p=kgTutorialPortable,snapshot=await store.snapshot();
      const helper=kgCreateTutorialSync({portable:p});
      await store.commitSnapshot(snapshot.records,await helper.stamps(snapshot.records),snapshot.records);
      const remote=JSON.parse(JSON.stringify(snapshot.records));remote[0].route.title='Phone revision';remote[0].revisionId='revision:phone';
      let bytes=p.exportCollection(remote),revision='remote-v1';
      kgCloudSyncConfig.googleDriveClientId='test-client';
      window.kgCreateGoogleDriveAuthorizer=()=>({connect:async()=>{},token:()=> 'test-token',disconnect:()=>{}});
      window.kgCreateGoogleDrivePersonalDataProvider=options=>options.fileName ? {
        read:async()=>({bytes,revision}),write:async value=>{bytes=value;revision='remote-v2';return {revision};}
      } : {};
      window.kgCreatePersonalDataSyncEngine=()=>({synchronize:async()=>({})});
      kgInitialiseGoogleDriveSync();
    }''',tutorial_id)
    if local_edit:
        page.locator('#kg_tutorial_editor_commentary').fill('Keep my current laptop narration.')
        _record(page,tutorial_id)
    commentary = page.locator('#kg_tutorial_editor_commentary')
    original_text = commentary.input_value()
    commentary.focus()
    commentary.evaluate('e=>{e.setSelectionRange(3,12);e.dataset.originalEditor="true";}')
    page.evaluate('document.getElementById("kg_cloud_sync_connect").click()')
    page.wait_for_function("document.getElementById('kg_cloud_sync_status').textContent.includes('Last synced')")
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')
    assert commentary.input_value() == original_text
    assert commentary.evaluate('e=>e===document.activeElement && e.selectionStart===3 && e.selectionEnd===12 && e.dataset.originalEditor==="true"')
    records = page.evaluate('(async()=> (await kgPersonalData.tutorials.snapshot()).records)()')
    assert any(r['route']['title']=='Phone revision' for r in records)
    assert any(r['route']['steps'][0]['commentary']==original_text for r in records)
    assert len(records) == 2
    assert not tutorial_graph.page_errors


@pytest.mark.browser
def test_personal_backup_includes_tutorials_and_old_backup_retains_them(tutorial_graph):
    import json, zipfile
    from pathlib import Path
    from test_personal_tutorials import _fill_draft
    from playwright.sync_api import expect
    page = _library(tutorial_graph)
    page.locator('#kg_tutorial_new').click()
    _fill_draft(page)
    tutorial_id = page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    page.keyboard.press('Escape')
    tutorial_graph.open_control_section('kg_personal_data_section')
    with page.expect_download() as captured:
        page.locator('#kg_personal_data_export').click()
    path = Path(captured.value.path())
    with zipfile.ZipFile(path) as archive:
        tutorials = json.loads(archive.read('tutorials.json'))
    assert tutorials['records'][0]['id'] == tutorial_id
    page.evaluate('''async id=>{
      const r=await kgPersonalData.tutorials.get(id);await kgPersonalData.tutorials.remove(id,r.revisionId);
    }''',tutorial_id)
    page.locator('#kg_personal_data_import_input').set_input_files(str(path))
    expect(page.locator('#kg_personal_data_import_dialog')).to_have_attribute('open','')
    page.locator('input[name="kg_personal_import_mode"][value="replace"]').check()
    page.once('dialog',lambda dialog:dialog.accept())
    with page.expect_navigation(wait_until='domcontentloaded'):
        page.locator('#kg_personal_data_import_apply').click()
    page.wait_for_function('(id)=>window.kgPersonalData && kgPersonalData.tutorials.get(id).then(r=>r&&!r.deletedAt)',arg=tutorial_id)
    assert not page.evaluate('(id)=>kgPersonalData.tutorials.get(id)',tutorial_id)['deletedAt']
    # Legacy profile-only replacement must not erase tutorials in the sidecar store.
    legacy = bytes(page.evaluate('Array.from(kgPersonalDataArchive.exportBytes(kgPersonalData.getSnapshot()))'))
    tutorial_graph.open_control_section('kg_personal_data_section')
    if not page.locator('#kg_controls').is_visible():page.locator('#kg_controls_toggle').click()
    page.locator('#kg_personal_data_import_input').set_input_files({'name':'legacy.zip','mimeType':'application/zip','buffer':legacy})
    expect(page.locator('#kg_personal_data_import_dialog')).to_have_attribute('open','')
    page.locator('input[name="kg_personal_import_mode"][value="replace"]').check()
    page.once('dialog',lambda dialog:dialog.accept())
    with page.expect_navigation(wait_until='domcontentloaded'):
        page.locator('#kg_personal_data_import_apply').click()
    page.wait_for_function('(id)=>window.kgPersonalData && kgPersonalData.tutorials.get(id).then(r=>r&&!r.deletedAt)',arg=tutorial_id)
    assert not page.evaluate('(id)=>kgPersonalData.tutorials.get(id)',tutorial_id)['deletedAt']


@pytest.mark.browser
def test_tutorial_import_review_cancel_replace_and_stale_revision(tutorial_graph):
    from playwright.sync_api import expect
    page = _library(tutorial_graph)
    original = page.evaluate('async()=>kgPersonalData.tutorials.create(tutorialData[0])')
    payload = bytes(page.evaluate('''id=>kgPersonalData.tutorials.get(id).then(r=>{
      r.route.title='Imported revision';return Array.from(kgTutorialPortable.exportSingle(r,true));
    })''',original['id']))
    upload = {'name':'tutorial.json','mimeType':'application/json','buffer':payload}
    page.locator('#kg_tutorial_import_file').set_input_files(upload)
    expect(page.locator('#kg_tutorial_import_dialog')).to_have_attribute('open','')
    page.locator('#kg_tutorial_import_cancel').click()
    assert page.evaluate('async()=> (await kgPersonalData.tutorials.list()).length') == 1
    page.locator('#kg_tutorial_import_file').set_input_files(upload)
    expect(page.locator('#kg_tutorial_import_dialog')).to_have_attribute('open','')
    page.locator('#kg_tutorial_import_replace').check()
    page.evaluate('''async id=>{const r=await kgPersonalData.tutorials.get(id);r.route.title='New local revision';await kgPersonalData.tutorials.save(r);}''',original['id'])
    page.locator('#kg_tutorial_import_apply').click()
    expect(page.locator('#kg_tutorial_import_status')).not_to_be_empty()
    assert page.evaluate('async()=> (await kgPersonalData.tutorials.list()).length') == 1
    assert page.evaluate('id=>kgPersonalData.tutorials.get(id)',original['id'])['route']['title']=='New local revision'
    page.locator('#kg_tutorial_import_cancel').click()
    page.locator('#kg_tutorial_import_file').set_input_files(upload)
    expect(page.locator('#kg_tutorial_import_dialog')).to_have_attribute('open','')
    page.locator('#kg_tutorial_import_replace').check()
    page.locator('#kg_tutorial_import_apply').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')
    records = page.evaluate('async()=>kgPersonalData.tutorials.list()')
    assert len(records)==2
    assert next(r for r in records if r['id']==original['id'])['route']['title']=='Imported revision'
    assert any(r['route']['title'].startswith('New local revision') for r in records)


@pytest.mark.browser
def test_full_backup_rejects_bad_tutorial_and_rolls_back_on_tutorial_write_failure(tutorial_graph):
    from playwright.sync_api import expect
    page = _library(tutorial_graph)
    before = page.evaluate('''async()=>{
      await kgPersonalData.tutorials.create(tutorialData[0]);
      const profile=kgPersonalData.getSnapshot(), records=(await kgPersonalData.tutorials.snapshot()).records;
      const files=kgTextZip.decode(kgPersonalDataArchive.exportBytes(profile,records));
      const invalid=JSON.parse(files['tutorials.json']);invalid.records[0].route.steps[0].action.command='run-script';
      files['tutorials.json']=JSON.stringify(invalid);
      window.__badBackup=Array.from(kgTextZip.encode(files));
      window.__goodBackup=Array.from(kgPersonalDataArchive.exportBytes(profile,records));
      return {profile,records};
    }''')
    tutorial_graph.open_control_section('kg_personal_data_section')
    invalid=bytes(page.evaluate('__badBackup'))
    page.locator('#kg_personal_data_import_input').set_input_files({'name':'bad.zip','mimeType':'application/zip','buffer':invalid})
    expect(page.locator('#kg_personal_data_status')).not_to_be_empty()
    assert not page.locator('#kg_personal_data_import_dialog').is_visible()
    assert page.evaluate('kgPersonalData.getSnapshot()') == before['profile']
    assert page.evaluate('async()=> (await kgPersonalData.tutorials.snapshot()).records') == before['records']
    valid=bytes(page.evaluate('__goodBackup'))
    page.evaluate("()=>{kgPersonalData.tutorials.commitSnapshot=()=>Promise.reject(new Error('Storage full'));}")
    page.locator('#kg_personal_data_import_input').set_input_files({'name':'good.zip','mimeType':'application/zip','buffer':valid})
    page.locator('#kg_personal_data_import_apply').click()
    expect(page.locator('#kg_personal_data_status')).to_contain_text('Import did not complete')
    restored=page.evaluate('kgPersonalData.getSnapshot()')
    for collection in ['notes','layout','studyResults','studyResets','readingProgress']:
        assert restored[collection] == before['profile'][collection]
    assert page.evaluate('async()=> (await kgPersonalData.tutorials.snapshot()).records') == before['records']


@pytest.mark.browser
def test_tutorial_drive_provider_reads_duplicates_caches_versions_and_rechecks_creation(tutorial_graph):
    page = _library(tutorial_graph)
    result = page.evaluate('''async()=>{
      const calls=[],files=[{id:'b',name:'PhysicsKG tutorials.zip',version:'1'},{id:'a',name:'PhysicsKG tutorials.zip',version:'1'}];
      const provider=kgCreateGoogleDrivePersonalDataProvider({fileName:'PhysicsKG tutorials.zip',allMatches:true,accessToken:'test',fetch:async(url,options)=>{
        calls.push({url,method:options.method||'GET',headers:options.headers});
        if(options.method==='PATCH')return new Response(JSON.stringify({id:'a',version:'2'}),{headers:{etag:'etag-2'}});
        if(url.includes('alt=media'))return new Response(new Uint8Array([url.includes('/a?')?1:2]),{headers:{etag:'etag-1'}});
        return new Response(JSON.stringify({files}));
      }});
      const first=await provider.read();await provider.read();
      await provider.write(new Uint8Array([3]),{revision:first.revision});
      files[1].version='2';await provider.read();
      let conflict=false;try{await provider.write(new Uint8Array([4]),{create:true});}catch(e){conflict=e.code==='conflict';}
      return {id:first.id,copies:first.copies.map(r=>r.id),calls,conflict};
    }''')
    assert result['id']=='a' and result['copies']==['b']
    assert result['conflict']
    assert sum('alt=media' in call['url'] for call in result['calls'])==3
    update=next(call for call in result['calls'] if call['method']=='PATCH')
    assert '/a?' in update['url'] and update['headers']['If-Match']=='etag-1'
    assert not any(call['method']=='POST' for call in result['calls'])


@pytest.mark.browser
def test_tutorial_sync_failure_reports_profile_success_without_touching_local_tutorials(tutorial_graph):
    from playwright.sync_api import expect
    page = _library(tutorial_graph)
    before=page.evaluate('''async()=>{
      await kgPersonalData.tutorials.create(tutorialData[0]);
      kgCloudSyncConfig.googleDriveClientId='test-client';
      window.kgCreateGoogleDriveAuthorizer=()=>({connect:async()=>{},token:()=> 'test',disconnect:()=>{}});
      window.kgCreateGoogleDrivePersonalDataProvider=options=>options.fileName ? {read:async()=>{throw new Error('Offline');}} : {};
      window.kgCreatePersonalDataSyncEngine=()=>({synchronize:async()=>({})});
      kgInitialiseGoogleDriveSync();return kgPersonalData.tutorials.snapshot();
    }''')
    tutorial_graph.open_control_section('kg_personal_data_section')
    page.locator('#kg_cloud_sync_connect').click()
    expect(page.locator('#kg_cloud_sync_status')).to_contain_text('tutorials are still pending')
    assert page.evaluate('async()=>kgPersonalData.tutorials.snapshot()') == before


@pytest.mark.browser
def test_full_import_reports_failure_in_dialog_and_cannot_cancel_in_flight(tutorial_graph):
    from playwright.sync_api import expect
    page = _library(tutorial_graph)
    payload = bytes(page.evaluate('''async()=>{
      const r=await kgPersonalData.tutorials.create(tutorialData[0]);
      const profile=kgPersonalData.getSnapshot();
      profile.readingProgress['2.1.definition']={blockId:'2.1.definition',isRead:true,updatedAt:'2026-11-17T12:00:00Z',deviceId:'import-test'};
      window.__beforeImport=kgPersonalData.getSnapshot();
      kgPersonalData.tutorials.commitSnapshot=()=>new Promise((resolve,reject)=>{window.__failImport=()=>reject(new Error('Storage full'));});
      return Array.from(kgPersonalDataArchive.exportBytes(profile,[r]));
    }'''))
    tutorial_graph.open_control_section('kg_personal_data_section')
    page.locator('#kg_personal_data_import_input').set_input_files({'name':'backup.zip','mimeType':'application/zip','buffer':payload})
    page.locator('#kg_personal_data_import_apply').click()
    page.wait_for_function('typeof __failImport==="function"')
    expect(page.locator('#kg_personal_data_import_cancel')).to_be_disabled()
    page.keyboard.press('Escape')
    expect(page.locator('#kg_personal_data_import_dialog')).to_have_attribute('open','')
    page.evaluate('__failImport()')
    expect(page.locator('#kg_personal_data_import_status')).to_be_visible()
    expect(page.locator('#kg_personal_data_import_status')).to_contain_text('Import did not complete')
    assert page.evaluate('kgPersonalData.getSnapshot().readingProgress') == page.evaluate('__beforeImport.readingProgress')
