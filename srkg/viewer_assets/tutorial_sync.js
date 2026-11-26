/* Whole-tutorial three-way merge. Conflict copies have stable IDs; no card-order merging. */
function kgCreateTutorialSync(options) {
  'use strict';
  var portable = options.portable;
  async function stamps(records) {
    var result = {};
    await Promise.all(records.map(async function(record) { result[record.id] = await portable.fingerprint(record); }));
    return result;
  }
  async function merge(local, remote, baseline) {
    baseline = baseline || {};
    var all = local.concat(remote).map(function(record) {
      return options.legacyProvider ? portable.syncRecord(record) : portable.record(record,true);
    });
    var hashes = await Promise.all(all.map(portable.fingerprint)), grouped = new Map(), resolved = new Set();
    all.forEach(function(record,index) {
      if (!grouped.has(record.id)) { grouped.set(record.id,new Map()); }
      grouped.get(record.id).set(hashes[index],record);
      if (record.conflictOf && record.sourceRevision) { resolved.add(record.conflictOf + ':' + record.sourceRevision); }
    });
    var localHashes = await stamps(local), result = new Map(), copies = [], relocations = {};
    grouped.forEach(function(candidates,id) {
      var items = Array.from(candidates.entries()).map(function(pair) { return {hash:pair[0],record:pair[1]}; });
      items = items.filter(function(item) {
        if (!resolved.has(id + ':' + item.hash)) { return true; }
        if (localHashes[id] === item.hash) { relocations[id] = 'personal:conflict-' + item.hash; }
        return false;
      });
      if (items.length > 1) { items = items.filter(function(item) { return item.hash !== baseline[id]; }); }
      if (!items.length) { return; }
      items.sort(function(a,b) {
        return Number(Boolean(a.record.deletedAt)) - Number(Boolean(b.record.deletedAt)) || a.hash.localeCompare(b.hash);
      });
      var winner = items[items.length - 1]; result.set(id,winner.record);
      items.slice(0,-1).forEach(function(item) {
        if (item.record.deletedAt) { return; }
        var copy = portable.clone(item.record), copyId = 'personal:conflict-' + item.hash;
        copy.id = copyId; copy.route.tutorial_id = copyId; copy.revisionId = 'conflict:' + item.hash;
        copy.conflictOf = id; copy.sourceRevision = item.hash;
        copies.push(copy);
        if (localHashes[id] === item.hash) { relocations[id] = copyId; }
      });
    });
    copies.forEach(function(copy) { if (!result.has(copy.id)) { result.set(copy.id,copy); } });
    return {records:Array.from(result.values()).sort(function(a,b) { return a.id.localeCompare(b.id); }),relocations:relocations};
  }
  function sameStamps(first, second) {
    return Object.keys(first).length === Object.keys(second).length &&
      Object.keys(first).every(function(id) { return first[id] === second[id]; });
  }
  async function readLegacy(legacyProvider) {
    var remote = await legacyProvider.read();
    var records = remote ? portable.importCollection(remote.bytes) : [];
    for (var extra of remote && remote.copies || []) {
      records = records.concat(portable.importCollection(extra.bytes));
    }
    return (await merge([],records,{})).records;
  }
  async function prepareAudio(records, store, provider) {
    var ids = new Set(), downloads = [];
    records.forEach(function(record) {
      if (record.deletedAt) { return; }
      record.route.steps.forEach(function(step) { if (step.audio) { ids.add(step.audio.assetId); } });
    });
    if (!ids.size) { return downloads; }
    var inventory = await provider.audioInventory();
    for (var id of ids) {
      var local = await store.getAudio(id), matches = inventory.get(id) || [];
      if (local && !matches.length) {
        await provider.uploadAudio(await portable.validateAudio(local.blob,id));
      } else if (!local) {
        var downloaded = null;
        for (var file of matches) {
          var blob = await provider.downloadAudio(file);
          if (!blob) { continue; }
          try { downloaded = await portable.validateAudio(blob,id); break; }
          catch (error) { /* Try another Drive copy of the same asset. */ }
        }
        if (!downloaded) { throw new Error('A tutorial recording is missing or damaged in Google Drive.'); }
        downloads.push(downloaded);
      }
    }
    return downloads;
  }
  var active = null;
  async function run() {
    var store = options.store, provider = options.provider, legacy = options.legacyProvider;
    if (!store || !provider) { throw new Error('Tutorial sync needs storage and a provider.'); }
    for (var attempt = 0; attempt < 3; attempt += 1) {
      if (options.prepare) { await options.prepare(); }
      var local = await store.snapshot();
      if (!legacy) { portable.requireTextOnly(local.records); }
      var remote = await provider.read();
      var decode = legacy ? portable.importCloudCollection : function(bytes) {
        return {records:portable.importCollection(bytes),legacyStamps:{}};
      };
      var cloud = remote ? decode(remote.bytes) : {records:[],legacyStamps:{}};
      var primary = cloud.records;
      var remoteRecords = primary.slice();
      for (var extra of remote && remote.copies || []) { remoteRecords = remoteRecords.concat(decode(extra.bytes).records); }
      var legacyStamps = cloud.legacyStamps, legacyChanged = false;
      var older = legacy ? await readLegacy(legacy) : [];
      if (legacy && !remote) { remoteRecords = remoteRecords.concat(older); }
      var merged = await merge(local.records,remoteRecords,local.baseline);
      if (legacy) {
        var olderStamps = await stamps(older);
        var changes = older.filter(function(record) { return olderStamps[record.id] !== legacyStamps[record.id]; });
        if (remote && changes.length) {
          var updated = await merge(merged.records,changes,legacyStamps);
          Object.entries(merged.relocations).forEach(function(pair) {
            updated.relocations[pair[0]] = updated.relocations[pair[1]] || pair[1];
          });
          merged.records = updated.records;
          merged.relocations = updated.relocations;
          legacyChanged = true;
        }
        legacyStamps = Object.assign({},legacyStamps,olderStamps);
      }
      if (!remote && !merged.records.length) { return {skipped:true, conflicts:0}; }
      var mergedStamps = await stamps(merged.records), primaryStamps = await stamps(primary);
      var equal = sameStamps(primaryStamps,mergedStamps) && sameStamps(cloud.legacyStamps,legacyStamps);
      try {
        var assets = legacy ? await prepareAudio(merged.records,store,provider) : [];
        if (!equal || !remote) {
          if (remote && !remote.revision) { throw new Error('Google Drive did not provide a revision; tutorial upload was stopped to protect the cloud copy.'); }
          var bytes = legacy ? portable.exportCloudCollection(merged.records,legacyStamps) : portable.exportCollection(merged.records);
          await provider.write(bytes, {revision:remote ? remote.revision : null,create:!remote});
        }
        if (options.prepare) { await options.prepare(); }
        await store.commitSnapshot(merged.records,mergedStamps,local.records,undefined,assets);
        if (options.updated) { await options.updated(merged); }
        var after = await store.snapshot(), afterStamps = await stamps(after.records);
        var pending = !sameStamps(afterStamps,mergedStamps);
        return {pending:pending,legacyChanged:legacyChanged,
          conflicts:merged.records.filter(function(record) { return !record.deletedAt && record.conflictOf; }).length};
      } catch (error) {
        if (!error || error.code !== 'conflict' || attempt === 2) { throw error; }
      }
    }
  }
  function synchronize() {
    if (active) { return active; }
    active = run().finally(function() { active = null; }); return active;
  }
  return {merge:merge, stamps:stamps, synchronize:synchronize};
}
