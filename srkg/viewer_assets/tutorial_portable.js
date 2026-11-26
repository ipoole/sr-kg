/* Validated tutorial archives and Drive library documents. */
function kgCreateTutorialPortable(options) {
  'use strict';
  var contract = options.contract, maxBytes = 10 * 1024 * 1024;
  function clone(value) { return JSON.parse(JSON.stringify(value)); }
  function object(value, label) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) { throw new Error(label + ' must be an object.'); }
    return value;
  }
  function keys(value, allowed, label) {
    object(value,label);
    Object.keys(value).forEach(function(key) { if (allowed.indexOf(key) < 0) { throw new Error('Unsupported ' + label + ' field: ' + key); } });
  }
  function text(value, label, maximum, required) {
    if (typeof value !== 'string' || value.length > maximum || (required && !value.trim())) { throw new Error('Invalid ' + label + '.'); }
    return value;
  }
  function identifier(value) { return typeof value === 'string' && /^[A-Za-z0-9_.:-]{1,300}$/.test(value); }
  function date(value, label) {
    if (typeof value !== 'string' || !/^\d{4}-\d\d-\d\dT/.test(value) || Number.isNaN(Date.parse(value))) { throw new Error('Invalid ' + label + '.'); }
    return new Date(value).toISOString();
  }
  function target(value, kind) {
    if (value === '' || value === null) { return; } // Incomplete drafts remain portable.
    var prefix = kind + ':';
    if (typeof value !== 'string' || value.indexOf(prefix) !== 0 || !identifier(value.slice(prefix.length))) {
      throw new Error('Invalid ' + kind + ' target.');
    }
  }
  function edge(value) {
    if (value === '' || value === null) { return; }
    var parts = typeof value === 'string' && value.indexOf('edge:') === 0 ? value.slice(5).split('|') : [];
    if (parts.length !== 3 || !identifier(parts[0]) || !identifier(parts[2]) || contract.relations.indexOf(parts[1]) < 0) { throw new Error('Invalid edge target.'); }
  }
  function pointer(value, sync) {
    if (value === '' || value === null) { return; }
    if (typeof value !== 'string') { throw new Error('Invalid pointer.'); }
    if (Object.prototype.hasOwnProperty.call(contract.pointer_base,value)) { return; }
    if (value.indexOf('control:module-fold:') === 0) { return target('module:' + value.slice(20),'module'); }
    if (value.indexOf('control:') === 0 && contract.controls.indexOf(value.slice(8)) >= 0) { return; }
    if (value.indexOf('tools:section:') === 0 && contract.tools.indexOf(value.slice(14)) >= 0) { return; }
    if (value.indexOf('graph:edge:') === 0) { return edge(value.slice(6)); }
    if (/^(graph|search):(concept|module):/.test(value)) {
      var rest = value.slice(value.indexOf(':') + 1); return target(rest, rest.split(':')[0]);
    }
    if (value.indexOf('details:block:') === 0) { return target(value.slice(8), 'block'); }
    var match = /^details:reading-(tree|sync|concept):([^:]+)(?::(.+))?$/.exec(value);
    if (match && contract.recipes.indexOf(match[2]) >= 0) {
      if (match[1] === 'concept') { return target('concept:' + (match[3] || ''),'concept'); }
      if (!match[3]) { return; }
    }
    // A saved draft or an older viewer can have a semantic pointer that this
    // viewer cannot resolve. Preserve it across devices without accepting selectors.
    if (sync && value.length <= 300 && /^(control|details|tools|graph|search):[A-Za-z0-9_.:-]*$/.test(value)) { return; }
    throw new Error('Unsupported pointer target.');
  }
  function command(value) {
    object(value,'Action');
    var spec = contract.commands[value.command];
    if (!spec) { throw new Error('Unsupported tutorial action: ' + value.command); }
    var allowed = ['command'].concat(spec.fields.map(function(field) { return field.name; }));
    if (value.command === 'set-context') { allowed.push('customTraversals'); }
    keys(value,allowed,'action');
    spec.fields.forEach(function(field) {
      var item = value[field.name];
      if (item === undefined || item === null) { return; }
      if (field.type === 'integer' || field.type === 'number') {
        if (typeof item !== 'number' || !Number.isFinite(item) || (field.type === 'number' && (item < field.min || item > field.max))) { throw new Error('Invalid numeric action field.'); }
      } else if (field.type === 'boolean') {
        if (typeof item !== 'boolean') { throw new Error('Invalid boolean action field.'); }
      } else if (field.type === 'object') {
        if (typeof item !== 'string' || !/^(concept|module):/.test(item)) {
          if (item !== '') { throw new Error('Invalid selection target.'); }
        } else { target(item,item.split(':')[0]); }
      } else if (field.type === 'edge') { edge(item); }
      else if (['concept','module','block'].indexOf(field.type) >= 0) { target(item,field.type); }
      else { text(item,field.label,field.max_length || 300,false); }
    });
    if (value.customTraversals !== undefined) {
      if (!Array.isArray(value.customTraversals) || value.customTraversals.length > 20) { throw new Error('Invalid custom context.'); }
      value.customTraversals.forEach(function(item) {
        keys(item,['relation','direction'],'context traversal');
        if (contract.relations.indexOf(item.relation) < 0 || ['incoming','outgoing','undirected'].indexOf(item.direction) < 0) { throw new Error('Invalid context traversal.'); }
      });
    }
  }
  function route(value, sync) {
    keys(value,['tutorial_id','title','summary','author','category','sequence','domains','steps'],'tutorial');
    if (!identifier(value.tutorial_id)) { throw new Error('Invalid tutorial ID.'); }
    text(value.title,'tutorial title',300,false); text(value.summary === undefined ? '' : value.summary,'tutorial summary',10000,false);
    if (value.author !== undefined) { text(value.author,'author credit',300,false); }
    if (['interface','physics'].indexOf(value.category) < 0 || !Number.isInteger(value.sequence)) { throw new Error('Invalid tutorial metadata.'); }
    if (!Array.isArray(value.domains) || value.domains.length > 100 || value.domains.some(function(id) { return !identifier(id); })) { throw new Error('Invalid domains.'); }
    if (!Array.isArray(value.steps) || value.steps.length > 1000) { throw new Error('Invalid card list.'); }
    var ids = new Set();
    function checkPointer(mark, cardIndex, actionIndex) {
      keys(mark,['target'],'pointer');
      try { pointer(mark.target,sync); }
      catch (error) {
        if (!sync) { throw error; }
        var detail = typeof mark.target === 'string' ? ' ' + JSON.stringify(mark.target.slice(0,100)) : '';
        throw new Error('Tutorial “' + (value.title || 'Untitled') + '”, card ' + (cardIndex + 1) +
          ', action ' + (actionIndex + 1) + ': ' + error.message + detail);
      }
    }
    value.steps.forEach(function(step, cardIndex) {
      keys(step,['step_id','title','commentary','prepare','action','actions','pointer','demonstrate','audio'],'card');
      if (step.audio !== undefined) {
        keys(step.audio,['assetId','duration','commentaryHash','actionsHash','mimeType'],'voice reference');
        if (!['assetId','commentaryHash','actionsHash'].every(function(key) { return /^[a-f0-9]{64}$/.test(step.audio[key]); }) ||
            (step.audio.mimeType !== undefined && !audioType(step.audio.mimeType)) || !Number.isFinite(step.audio.duration) || step.audio.duration <= 0) { throw new Error('Invalid voice reference.'); }
      }
      if (step.demonstrate !== undefined && typeof step.demonstrate !== 'boolean') { throw new Error('Invalid demonstration flag.'); }
      if (!identifier(step.step_id) || ids.has(step.step_id)) { throw new Error('Invalid or duplicate card ID.'); }
      ids.add(step.step_id); text(step.title,'card title',300,false); text(step.commentary === undefined ? '' : step.commentary,'written narration',100000,false);
      if (step.prepare !== undefined) {
        if (!Array.isArray(step.prepare) || step.prepare.length > 100) { throw new Error('Invalid setup action list.'); }
        step.prepare.forEach(command);
      }
      if (step.actions !== undefined) {
        if (step.action !== undefined || step.pointer !== undefined || !Array.isArray(step.actions) || !step.actions.length || step.actions.length > contract.max_actions) { throw new Error('Invalid action sequence.'); }
        step.actions.forEach(function(item, actionIndex) {
          keys(item,['action','pointer','pause_ms'],'visible action'); command(item.action);
          if (item.pause_ms !== undefined && (typeof item.pause_ms !== 'number' || !Number.isFinite(item.pause_ms))) { throw new Error('Invalid action pause.'); }
          if (item.pointer !== undefined) { checkPointer(item.pointer,cardIndex,actionIndex); }
        });
      } else {
        command(step.action);
        if (step.pointer !== undefined) { checkPointer(step.pointer,cardIndex,0); }
      }
    });
    var result = clone(value);
    if (result.summary === undefined) { result.summary = ''; }
    result.steps.forEach(function(step) { if (step.commentary === undefined) { step.commentary = ''; } });
    return result;
  }
  function record(value, personal, sync) {
    keys(value,['id','route','basedOn','createdAt','updatedAt','revisionId','deletedAt','conflictOf','sourceRevision'],'tutorial record');
    var result = clone(value); result.route = route(value.route,sync);
    if (!identifier(value.id) || (personal && value.id.indexOf('personal:') !== 0) || value.route.tutorial_id !== value.id || !identifier(value.revisionId)) { throw new Error('Invalid tutorial record identity.'); }
    result.createdAt = date(value.createdAt,'creation time'); result.updatedAt = date(value.updatedAt,'update time');
    result.deletedAt = value.deletedAt ? date(value.deletedAt,'deletion time') : '';
    if (value.basedOn) {
      keys(value.basedOn,['tutorialId','version'],'source credit');
      text(value.basedOn.tutorialId,'source tutorial ID',300,true); text(value.basedOn.version,'source version',100,true);
    }
    ['conflictOf','sourceRevision'].forEach(function(key) { if (value[key] !== undefined) { text(value[key],key,300,true); } });
    return result;
  }
  function collection(value, sync) {
    keys(value,['format','schema_version','records'],'tutorial library');
    if (value.format !== 'physicskg-tutorial-library' || value.schema_version !== 1 || !Array.isArray(value.records) || value.records.length > 1000) { throw new Error('Unsupported tutorial library.'); }
    var ids = new Set();
    return value.records.map(function(item) {
      var checked = record(item,true,sync);
      if (ids.has(checked.id)) { throw new Error('Duplicate tutorial record.'); } ids.add(checked.id); return checked;
    });
  }
  function requireTextOnly(records) {
    if (records.some(function(record) { return record.route.steps.some(function(step) { return Boolean(step.audio); }); })) {
      throw new Error('This format is text-only. Use Export tutorial for a voiced ZIP.');
    }
  }
  function collectionDocument(records) { requireTextOnly(records); return {format:'physicskg-tutorial-library', schema_version:1, records:records}; }
  function parse(textValue) {
    if (typeof textValue !== 'string' || new TextEncoder().encode(textValue).length > maxBytes) { throw new Error('Tutorial package exceeds 10 MB.'); }
    return JSON.parse(textValue.replace(/^\uFEFF/,''));
  }
  function json(value) { var result = JSON.stringify(value,null,2) + '\n'; parse(result); return result; }
  function unpack(buffer) {
    var bytes = new Uint8Array(buffer);
    if (bytes.length > maxBytes) { throw new Error('Tutorial package exceeds 10 MB.'); }
    if (bytes[0] === 0x50 && bytes[1] === 0x4b) { return kgTextZip.decode(bytes); }
    return {'tutorial.json':new TextDecoder('utf-8',{fatal:true}).decode(bytes)};
  }
  function checkManifest(files, format, definition) {
    var allowed = ['manifest.json',definition];
    if (Object.keys(files).some(function(name) { return allowed.indexOf(name) < 0; })) { throw new Error('Unexpected file in tutorial package.'); }
    if (!files[definition]) { throw new Error('Tutorial definition is missing.'); }
    if (files['manifest.json']) {
      var manifest = parse(files['manifest.json']);
      if (manifest.format !== format || manifest.schema_version !== 1 || manifest.route_schema_version !== 1 ||
          !Array.isArray(manifest.assets) || manifest.assets.length) { throw new Error('Unsupported tutorial package version or audio.'); }
    } else if (definition !== 'tutorial.json') { throw new Error('Tutorial manifest is missing.'); }
  }
  function manifest(format) { return json({format:format,schema_version:1,route_schema_version:1,assets:[]}); }
  function exportSingle(value, asJson) {
    requireTextOnly([value]);
    var checked = record(value,false);
    var definition = json({format:'physicskg-tutorial',schema_version:1,route_schema_version:1,tutorial:checked});
    return asJson ? new TextEncoder().encode(definition) : kgTextZip.encode({'manifest.json':manifest('physicskg-tutorial'),'tutorial.json':definition});
  }
  function importSingle(buffer) {
    var files = unpack(buffer); checkManifest(files,'physicskg-tutorial','tutorial.json');
    var value = parse(files['tutorial.json']);
    if (value.format !== 'physicskg-tutorial' || value.schema_version !== 1 || value.route_schema_version !== 1) { throw new Error('Unsupported tutorial definition.'); }
    var checked = record(value.tutorial,false); requireTextOnly([checked]); return checked;
  }
  var bundleLimit = 200 * 1024 * 1024, clipLimit = 50 * 1024 * 1024;
  function voiceCards(route) { return route.steps.filter(function(step) { return step.audio; }); }
  function assetPath(id) { return 'audio/' + id; }
  function audioType(type) {
    return typeof type === 'string' && type.length <= 128 &&
      /^audio\/[a-z0-9.+-]+(?:;[a-z0-9=., +_-]+)?$/i.test(type);
  }
  async function sha256(bytes) {
    var result = await crypto.subtle.digest('SHA-256',bytes);
    return Array.from(new Uint8Array(result)).map(function(byte) { return byte.toString(16).padStart(2,'0'); }).join('');
  }
  async function exportBundle(source, getAudio) {
    var checked = record(source,false), cards = voiceCards(checked.route);
    if (!cards.length) { return {bytes:exportSingle(checked,false), count:0}; }
    var files = {}, inventory = [], seen = new Set(), size = 0;
    for (var step of cards) {
      var id = step.audio.assetId;
      if (seen.has(id)) { continue; }
      var asset = await getAudio(id);
      if (!asset || !asset.blob || !asset.blob.size) { throw new Error('Recording is missing for “' + step.title + '”.'); }
      var blob = asset.blob;
      if (!audioType(blob.type) || blob.size > clipLimit) { throw new Error('Invalid audio for “' + step.title + '”.'); }
      size += blob.size;
      if (size > bundleLimit) { throw new Error('Tutorial package exceeds 200 MB.'); }
      var bytes = new Uint8Array(await blob.arrayBuffer());
      if (await sha256(bytes) !== id) { throw new Error('Recording checksum failed for “' + step.title + '”.'); }
      seen.add(id); files[assetPath(id)] = bytes;
      inventory.push({id:id, mimeType:blob.type, byteLength:blob.size});
    }
    var header = {format:'physicskg-tutorial', schema_version:2, route_schema_version:2};
    files['manifest.json'] = json(Object.assign({},header,{assets:inventory}));
    files['tutorial.json'] = json(Object.assign({},header,{tutorial:checked}));
    return {bytes:kgTextZip.encode(files,bundleLimit),count:cards.length};
  }
  async function importBundle(buffer) {
    var bytes = new Uint8Array(buffer);
    if (bytes[0] !== 0x50 || bytes[1] !== 0x4b) { return {source:importSingle(bytes),assets:[]}; }
    var files = kgTextZip.decode(bytes,true,bundleLimit);
    var decoder = new TextDecoder('utf-8',{fatal:true});
    var header = files['manifest.json'] && parse(decoder.decode(files['manifest.json']));
    if (!header || header.schema_version === 1) { return {source:importSingle(bytes),assets:[]}; }
    function current(value) {
      return value.format === 'physicskg-tutorial' && value.schema_version === 2 && value.route_schema_version === 2;
    }
    if (!current(header) || !Array.isArray(header.assets) || !files['tutorial.json']) {
      throw new Error('Unsupported voiced tutorial manifest.');
    }
    var definition = parse(decoder.decode(files['tutorial.json']));
    if (!current(definition)) { throw new Error('Unsupported voiced tutorial definition.'); }
    var source = record(definition.tutorial,false);
    var required = new Set(voiceCards(source.route).map(function(step) { return step.audio.assetId; }));
    if (Object.keys(files).length !== required.size + 2 || header.assets.length !== required.size) {
      throw new Error('Tutorial audio inventory does not match its cards.');
    }
    var assets = [];
    for (var entry of header.assets) {
      keys(entry,['id','mimeType','byteLength'],'audio asset');
      if (!required.delete(entry.id) || !audioType(entry.mimeType)) { throw new Error('Invalid tutorial audio inventory.'); }
      var data = files[assetPath(entry.id)];
      if (!data || !data.length || data.length > clipLimit || data.length !== entry.byteLength ||
          await sha256(data) !== entry.id) { throw new Error('Missing or damaged tutorial audio.'); }
      assets.push({id:entry.id,mimeType:entry.mimeType,byteLength:data.length,blob:new Blob([data],{type:entry.mimeType})});
    }
    return {source:source,assets:assets};
  }
  function exportCollection(records) {
    var value = collectionDocument(records); collection(value);
    return kgTextZip.encode({'manifest.json':manifest('physicskg-tutorial-library'),'tutorials.json':json(value)});
  }
  function importCollection(buffer) {
    var files = unpack(buffer); checkManifest(files,'physicskg-tutorial-library','tutorials.json');
    var checked = collection(parse(files['tutorials.json'])); requireTextOnly(checked); return checked;
  }
  function cloudCollection(value) {
    keys(value,['format','schema_version','records','legacyStamps'],'cloud tutorial library');
    if (value.format !== 'physicskg-cloud-tutorial-library' || value.schema_version !== 2 ||
        !value.legacyStamps || Array.isArray(value.legacyStamps) || typeof value.legacyStamps !== 'object' ||
        Object.entries(value.legacyStamps).some(function(pair) {
          return !pair[0].startsWith('personal:') || !/^[a-f0-9]{64}$/.test(pair[1]);
        })) { throw new Error('Unsupported cloud tutorial library.'); }
    return {records:collection({format:'physicskg-tutorial-library',schema_version:1,records:value.records},true),
      legacyStamps:value.legacyStamps};
  }
  function exportCloudCollection(records, legacyStamps) {
    var value = {format:'physicskg-cloud-tutorial-library',schema_version:2,records:records,legacyStamps:legacyStamps};
    cloudCollection(value);
    return new TextEncoder().encode(json(value));
  }
  function importCloudCollection(buffer) {
    if (buffer.byteLength > maxBytes) { throw new Error('Cloud tutorial library exceeds 10 MB.'); }
    return cloudCollection(parse(new TextDecoder('utf-8',{fatal:true}).decode(buffer)));
  }
  async function validateAudio(blob, id) {
    if (!blob || !blob.size || blob.size > clipLimit || !audioType(blob.type) ||
        await sha256(await blob.arrayBuffer()) !== id) {
      throw new Error('A tutorial recording is missing or damaged.');
    }
    return {id:id,mimeType:blob.type,byteLength:blob.size,blob:blob};
  }
  function stable(value) {
    if (Array.isArray(value)) { return '[' + value.map(stable).join(',') + ']'; }
    if (value && typeof value === 'object') { return '{' + Object.keys(value).sort().map(function(key) { return JSON.stringify(key) + ':' + stable(value[key]); }).join(',') + '}'; }
    return JSON.stringify(value);
  }
  async function fingerprint(value) {
    var bytes = new TextEncoder().encode(stable(value));
    var result = await crypto.subtle.digest('SHA-256',bytes);
    return Array.from(new Uint8Array(result)).map(function(byte) { return byte.toString(16).padStart(2,'0'); }).join('');
  }
  return {exportBundle:exportBundle, importBundle:importBundle, bundleLimit:bundleLimit, requireTextOnly:requireTextOnly, route:route, record:record, collection:collection, collectionDocument:collectionDocument,
    parse:parse, json:json, exportSingle:exportSingle, importSingle:importSingle,
    exportCollection:exportCollection, importCollection:importCollection,
    exportCloudCollection:exportCloudCollection, importCloudCollection:importCloudCollection,
    syncRecord:function(value) { return record(value,true,true); },
    validateAudio:validateAudio, fingerprint:fingerprint, clone:clone};
}
