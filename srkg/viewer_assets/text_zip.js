/* Stored UTF-8 ZIP files shared by personal-data and tutorial packages. */
(function(global) {
  "use strict";
  var crcTable = null;
  function crc32(bytes) {
    if (!crcTable) {
      crcTable = [];
      for (var n = 0; n < 256; n += 1) {
        var c = n;
        for (var k = 0; k < 8; k += 1) { c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; }
        crcTable[n] = c >>> 0;
      }
    }
    var crc = 0xffffffff;
    for (var i = 0; i < bytes.length; i += 1) {
      crc = crcTable[(crc ^ bytes[i]) & 0xff] ^ (crc >>> 8);
    }
    return (crc ^ 0xffffffff) >>> 0;
  }

  function u16(value) { return [value & 255, value >>> 8 & 255]; }
  function u32(value) { return [value & 255, value >>> 8 & 255, value >>> 16 & 255, value >>> 24 & 255]; }
  function join(parts) {
    var length = parts.reduce(function(total, item) { return total + item.length; }, 0);
    var result = new Uint8Array(length), offset = 0;
    parts.forEach(function(item) { result.set(item, offset); offset += item.length; });
    return result;
  }

  function makeZip(files, byteLimit) {
    if (Object.keys(files).length > 1000) { throw new Error('Archive contains too many files'); }
    var encoder = new TextEncoder(), locals = [], centrals = [], offset = 0, count = 0;
    Object.keys(files).forEach(function(name) {
      var nameBytes = encoder.encode(name), data = typeof files[name] === "string" ? encoder.encode(files[name]) : files[name];
      var crc = crc32(data), size = data.length;
      var local = new Uint8Array([
        0x50,0x4b,0x03,0x04].concat(u16(20),u16(0x0800),u16(0),u16(0),u16(0),
          u32(crc),u32(size),u32(size),u16(nameBytes.length),u16(0)));
      locals.push(local, nameBytes, data);
      var central = new Uint8Array([
        0x50,0x4b,0x01,0x02].concat(u16(20),u16(20),u16(0x0800),u16(0),u16(0),u16(0),
          u32(crc),u32(size),u32(size),u16(nameBytes.length),u16(0),u16(0),u16(0),u16(0),
          u32(0),u32(offset)));
      centrals.push(central, nameBytes);
      offset += local.length + nameBytes.length + data.length;
      count += 1;
    });
    var centralBytes = join(centrals);
    var end = new Uint8Array([
      0x50,0x4b,0x05,0x06].concat(u16(0),u16(0),u16(count),u16(count),
        u32(centralBytes.length),u32(offset),u16(0)));
    if (offset + centralBytes.length + end.length > (byteLimit || 20 * 1024 * 1024)) { throw new Error('Archive exceeds the size limit'); }
    return join(locals.concat([centralBytes, end]));
  }

  function readZip(buffer, binary, byteLimit) {
    var bytes = new Uint8Array(buffer);
    if (bytes.length > (byteLimit || 20 * 1024 * 1024)) { throw new Error('Archive exceeds the size limit'); }
    var view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    function d16(at) { return view.getUint16(at, true); }
    function d32(at) { return view.getUint32(at, true); }
    var end = -1;
    for (var i = bytes.length - 22; i >= Math.max(0, bytes.length - 65557); i -= 1) {
      if (d32(i) === 0x06054b50) { end = i; break; }
    }
    if (end < 0) { throw new Error("Not a supported ZIP archive"); }
    var count = d16(end + 10), cursor = d32(end + 16), decoder = new TextDecoder("utf-8", {fatal:true}), files = Object.create(null);
    if (count > 1000) { throw new Error('Archive contains too many files'); }
    for (var entry = 0; entry < count; entry += 1) {
      if (d32(cursor) !== 0x02014b50) { throw new Error("Invalid ZIP directory"); }
      var method = d16(cursor + 10), size = d32(cursor + 24);
      var nameLength = d16(cursor + 28), extraLength = d16(cursor + 30), commentLength = d16(cursor + 32);
      var localOffset = d32(cursor + 42);
      var name = decoder.decode(bytes.slice(cursor + 46, cursor + 46 + nameLength));
      if (!name || name.indexOf('\\') >= 0 || name.split('/').some(function(part) { return !part || part === '..' || part === '.'; }) ||
          Object.prototype.hasOwnProperty.call(files, name)) { throw new Error('Invalid or duplicate archive path'); }
      if (method !== 0 || d32(localOffset) !== 0x04034b50) {
        throw new Error("Archive must use uncompressed ZIP entries");
      }
      var localNameLength = d16(localOffset + 26), localExtraLength = d16(localOffset + 28);
      var start = localOffset + 30 + localNameLength + localExtraLength;
      if (start + size > bytes.length) { throw new Error("ZIP entry is truncated"); }
      var data = bytes.slice(start, start + size);
      if (crc32(data) !== d32(cursor + 16)) { throw new Error('ZIP checksum does not match'); }
      if (decoder.decode(bytes.slice(localOffset + 30, localOffset + 30 + localNameLength)) !== name ||
          d16(localOffset + 8) !== method || d32(localOffset + 18) !== size || d32(cursor + 20) !== size) {
        throw new Error('ZIP directory does not match file data');
      }
      files[name] = binary ? data : decoder.decode(data);
      cursor += 46 + nameLength + extraLength + commentLength;
    }
    return files;
  }

  global.kgTextZip = {encode:makeZip, decode:readZip};
})(window);
