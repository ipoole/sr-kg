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
    var all = local.concat(remote).map(function(record) { return portable.record(record,true); });
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
  var active = null;
  async function run() {
    var store = options.store, provider = options.provider;
    if (!store || !provider) { throw new Error('Tutorial sync needs storage and a provider.'); }
    for (var attempt = 0; attempt < 3; attempt += 1) {
      if (options.prepare) { await options.prepare(); }
      var local = await store.snapshot(), remote = await provider.read();
      var primary = remote ? portable.importCollection(remote.bytes) : [];
      var remoteRecords = primary.slice();
      for (var extra of remote && remote.copies || []) { remoteRecords = remoteRecords.concat(portable.importCollection(extra.bytes)); }
      var merged = await merge(local.records,remoteRecords,local.baseline);
      if (!remote && !merged.records.length) { return {skipped:true, conflicts:0}; }
      var mergedStamps = await stamps(merged.records), primaryStamps = await stamps(primary);
      var equal = Object.keys(primaryStamps).length === Object.keys(mergedStamps).length &&
        Object.keys(mergedStamps).every(function(id) { return mergedStamps[id] === primaryStamps[id]; });
      try {
        if (!equal || !remote) {
          if (remote && !remote.revision) { throw new Error('Google Drive did not provide a revision; tutorial upload was stopped to protect the cloud copy.'); }
          await provider.write(portable.exportCollection(merged.records), {revision:remote ? remote.revision : null,create:!remote});
        }
        if (options.prepare) { await options.prepare(); }
        await store.commitSnapshot(merged.records,mergedStamps,local.records);
        if (options.updated) { await options.updated(merged); }
        var after = await store.snapshot(), afterStamps = await stamps(after.records);
        var pending = Object.keys(afterStamps).length !== Object.keys(mergedStamps).length ||
          Object.keys(afterStamps).some(function(id) { return afterStamps[id] !== mergedStamps[id]; });
        return {pending:pending,conflicts:merged.records.filter(function(record) { return !record.deletedAt && record.conflictOf; }).length};
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
