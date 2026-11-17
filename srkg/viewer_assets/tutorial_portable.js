/* Transparent text-only tutorial packages; imported content never supplies executable selectors. */
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
  function pointer(value) {
    if (value === '' || value === null || contract.pointer_base[value]) { return; }
    if (typeof value !== 'string') { throw new Error('Invalid pointer.'); }
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
      if (field.type === 'integer') {
        if (typeof item !== 'number' || !Number.isFinite(item)) { throw new Error('Invalid numeric action field.'); }
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
  function route(value) {
    keys(value,['tutorial_id','title','summary','author','category','sequence','domains','steps'],'tutorial');
    if (!identifier(value.tutorial_id)) { throw new Error('Invalid tutorial ID.'); }
    text(value.title,'tutorial title',300,false); text(value.summary,'tutorial summary',10000,false);
    if (value.author !== undefined) { text(value.author,'author credit',300,false); }
    if (['interface','physics'].indexOf(value.category) < 0 || !Number.isInteger(value.sequence)) { throw new Error('Invalid tutorial metadata.'); }
    if (!Array.isArray(value.domains) || value.domains.length > 100 || value.domains.some(function(id) { return !identifier(id); })) { throw new Error('Invalid domains.'); }
    if (!Array.isArray(value.steps) || value.steps.length > 1000) { throw new Error('Invalid card list.'); }
    var ids = new Set();
    value.steps.forEach(function(step) {
      keys(step,['step_id','title','commentary','prepare','action','actions','pointer','demonstrate'],'card');
      if (step.demonstrate !== undefined && typeof step.demonstrate !== 'boolean') { throw new Error('Invalid demonstration flag.'); }
      if (!identifier(step.step_id) || ids.has(step.step_id)) { throw new Error('Invalid or duplicate card ID.'); }
      ids.add(step.step_id); text(step.title,'card title',300,false); text(step.commentary,'written narration',100000,false);
      if (step.prepare !== undefined) {
        if (!Array.isArray(step.prepare) || step.prepare.length > 100) { throw new Error('Invalid setup action list.'); }
        step.prepare.forEach(command);
      }
      if (step.actions !== undefined) {
        if (step.action !== undefined || step.pointer !== undefined || !Array.isArray(step.actions) || !step.actions.length || step.actions.length > contract.max_actions) { throw new Error('Invalid action sequence.'); }
        step.actions.forEach(function(item) {
          keys(item,['action','pointer','pause_ms'],'visible action'); command(item.action);
          if (item.pause_ms !== undefined && (typeof item.pause_ms !== 'number' || !Number.isFinite(item.pause_ms))) { throw new Error('Invalid action pause.'); }
          if (item.pointer !== undefined) { keys(item.pointer,['target'],'pointer'); pointer(item.pointer.target); }
        });
      } else {
        command(step.action);
        if (step.pointer !== undefined) { keys(step.pointer,['target'],'pointer'); pointer(step.pointer.target); }
      }
    });
    return clone(value);
  }
  function record(value, personal) {
    keys(value,['id','route','basedOn','createdAt','updatedAt','revisionId','deletedAt','conflictOf','sourceRevision'],'tutorial record');
    var result = clone(value); result.route = route(value.route);
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
  function collection(value) {
    keys(value,['format','schema_version','records'],'tutorial library');
    if (value.format !== 'physicskg-tutorial-library' || value.schema_version !== 1 || !Array.isArray(value.records) || value.records.length > 1000) { throw new Error('Unsupported tutorial library.'); }
    var ids = new Set();
    return value.records.map(function(item) {
      var checked = record(item,true);
      if (ids.has(checked.id)) { throw new Error('Duplicate tutorial record.'); } ids.add(checked.id); return checked;
    });
  }
  function collectionDocument(records) { return {format:'physicskg-tutorial-library', schema_version:1, records:records}; }
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
    var checked = record(value,false);
    var definition = json({format:'physicskg-tutorial',schema_version:1,route_schema_version:1,tutorial:checked});
    return asJson ? new TextEncoder().encode(definition) : kgTextZip.encode({'manifest.json':manifest('physicskg-tutorial'),'tutorial.json':definition});
  }
  function importSingle(buffer) {
    var files = unpack(buffer); checkManifest(files,'physicskg-tutorial','tutorial.json');
    var value = parse(files['tutorial.json']);
    if (value.format !== 'physicskg-tutorial' || value.schema_version !== 1 || value.route_schema_version !== 1) { throw new Error('Unsupported tutorial definition.'); }
    return record(value.tutorial,false);
  }
  function exportCollection(records) {
    var value = collectionDocument(records); collection(value);
    return kgTextZip.encode({'manifest.json':manifest('physicskg-tutorial-library'),'tutorials.json':json(value)});
  }
  function importCollection(buffer) {
    var files = unpack(buffer); checkManifest(files,'physicskg-tutorial-library','tutorials.json');
    return collection(parse(files['tutorials.json']));
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
  return {route:route, record:record, collection:collection, collectionDocument:collectionDocument,
    parse:parse, json:json, exportSingle:exportSingle, importSingle:importSingle,
    exportCollection:exportCollection, importCollection:importCollection, fingerprint:fingerprint, clone:clone};
}
