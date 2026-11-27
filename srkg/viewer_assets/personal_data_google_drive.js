(function(global) {
  "use strict";

  var DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.file";
  var DRIVE_API = "https://www.googleapis.com/drive/v3/files";
  var DRIVE_UPLOAD_API = "https://www.googleapis.com/upload/drive/v3/files";
  var DEFAULT_FILE_NAME = "PhysicsKG personal data.zip";

  function apiError(response, fallback) {
    var error = new Error(fallback || "Google Drive request failed");
    error.status = response.status;
    if (response.status === 401 || response.status === 403) { error.code = "auth_required"; }
    if (response.status === 409 || response.status === 412) { error.code = "conflict"; }
    return error;
  }

  function loadIdentityServices() {
    if (global.google && global.google.accounts && global.google.accounts.oauth2) {
      return Promise.resolve(global.google);
    }
    if (global.kgGoogleIdentityPromise) { return global.kgGoogleIdentityPromise; }
    global.kgGoogleIdentityPromise = new Promise(function(resolve, reject) {
      var existing = document.getElementById("kg_google_identity_script");
      var script = existing || document.createElement("script");
      function ready() {
        if (global.google && global.google.accounts && global.google.accounts.oauth2) {
          resolve(global.google);
        } else {
          reject(new Error("Google sign-in did not load"));
        }
      }
      script.addEventListener("load", ready, {once: true});
      script.addEventListener("error", function() {
        reject(new Error("Could not load Google sign-in"));
      }, {once: true});
      if (!existing) {
        script.id = "kg_google_identity_script";
        script.src = "https://accounts.google.com/gsi/client";
        script.async = true;
        document.head.appendChild(script);
      }
    });
    return global.kgGoogleIdentityPromise;
  }

  function createAuthorizer(options) {
    options = options || {};
    var clientId = String(options.clientId || "");
    var accessToken = "";
    var expiresAt = 0;

    function connect() {
      if (!clientId) { return Promise.reject(new Error("Google Drive sync is not configured")); }
      return loadIdentityServices().then(function(google) {
        return new Promise(function(resolve, reject) {
          var client = google.accounts.oauth2.initTokenClient({
            client_id: clientId,
            scope: DRIVE_SCOPE,
            callback: function(response) {
              if (!response || response.error || !response.access_token) {
                reject(new Error(response && response.error_description || "Google sign-in was cancelled"));
                return;
              }
              accessToken = response.access_token;
              expiresAt = Date.now() + Math.max(0, Number(response.expires_in) || 0) * 1000;
              resolve();
            }
          });
          client.requestAccessToken({prompt: "consent"});
        });
      });
    }

    function token() {
      if (!accessToken || (expiresAt && Date.now() >= expiresAt - 30000)) {
        var error = new Error("Google sign-in is required");
        error.code = "auth_required";
        throw error;
      }
      return accessToken;
    }

    function disconnect() {
      var tokenToRevoke = accessToken;
      accessToken = "";
      expiresAt = 0;
      if (tokenToRevoke && global.google && global.google.accounts && global.google.accounts.oauth2) {
        // Remote revocation is best effort; local disconnect must work offline.
        try { global.google.accounts.oauth2.revoke(tokenToRevoke, function() {}); }
        catch (error) { /* Local credentials have already been cleared. */ }
      }
    }

    return {connect: connect, token: token, disconnect: disconnect};
  }

  function createProvider(options) {
    options = options || {};
    var fetchImpl = options.fetch || global.fetch.bind(global);
    var token = typeof options.token === "function" ? options.token : function() {
      return String(options.accessToken || "");
    };
    var fileName = String(options.fileName || DEFAULT_FILE_NAME);
    var mimeType = options.mimeType || 'application/zip';
    var appendOnly = options.appendOnly === true;
    var snapshotName = 'PhysicsKG tutorial library snapshot.json';
    var fileId = "", allMatches = appendOnly || options.allMatches === true, cache = new Map();

    function headers(extra) {
      var result = {Authorization: "Bearer " + token()};
      Object.keys(extra || {}).forEach(function(key) { result[key] = extra[key]; });
      return result;
    }

    async function findMatches() {
      var escapedName = fileName.replace(/'/g, "\\'");
      var names = "name = '" + escapedName + "'";
      if (appendOnly) { names = "(" + names + " or name = '" + snapshotName + "')"; }
      var params = new URLSearchParams({q:names + " and trashed = false",spaces:'drive',
        fields:'nextPageToken,files(id,name,version,modifiedTime' + (appendOnly ? ',appProperties)' : ')'),
        orderBy:'modifiedTime desc',pageSize:appendOnly ? '1000' : allMatches ? '100' : '10'});
      var matches = [];
      do {
        var response = await fetchImpl(DRIVE_API + '?' + params.toString(),{headers:headers()});
        if (!response.ok) { throw apiError(response,'Could not search Google Drive'); }
        var result = await response.json();
        matches = matches.concat(result.files || []);
        if (!appendOnly) {
          if (allMatches && result.nextPageToken) { throw new Error('Too many duplicate tutorial cloud files; tidy them in Google Drive before syncing.'); }
          break;
        }
        if (result.nextPageToken) { params.set('pageToken',result.nextPageToken); }
      } while (result.nextPageToken);
      return matches.filter(function(item) { return item.name === fileName || appendOnly && item.name === snapshotName; });
    }
    function snapshotKey(file) {
      return file.name === snapshotName ? file.id : file.id + ':' + (file.version || '');
    }
    function snapshotHeads(files) {
      var covered = new Set();
      files.forEach(function(file) {
        if (file.name !== snapshotName) { return; }
        Object.entries(file.appProperties || {}).forEach(function(pair) {
          if (/^parent[0-9]+$/.test(pair[0])) { covered.add(pair[1]); }
        });
      });
      return files.filter(function(file) { return !covered.has(snapshotKey(file)); });
    }
    async function readFile(file) {
      var previous = cache.get(file.id);
      if (allMatches && previous && file.version && previous.version === file.version) { return previous.value; }
      var response = await fetchImpl(DRIVE_API + '/' + encodeURIComponent(file.id) + '?alt=media',{headers:headers()});
      if (response.status === 404) { cache.delete(file.id); return null; }
      if (!response.ok) { throw apiError(response,'Could not download ' + fileName); }
      var value = {id:file.id,bytes:await response.arrayBuffer(),revision:response.headers.get('etag') || ''};
      if (allMatches) { cache.set(file.id,{version:file.version,value:value}); }
      return value;
    }
    async function read() {
      var matches = !allMatches && fileId ? [{id:fileId}] : await findMatches();
      if (appendOnly && matches.length) {
        var heads = snapshotHeads(matches);
        if (!heads.length) { throw new Error('Google Drive has no current tutorial snapshot.'); }
        matches = heads;
        var ids = new Set(heads.map(function(file) { return file.id; }));
        cache.forEach(function(value,id) { if (!ids.has(id)) { cache.delete(id); } });
      }
      if (!matches.length) { return null; }
      if (allMatches) { matches.sort(function(a,b) { return a.id.localeCompare(b.id); }); }
      var available = [];
      for (var file of matches) { var value = await readFile(file); if (value) { available.push(value); } }
      if (appendOnly && available.length !== matches.length) {
        var changed = new Error('Google Drive tutorial snapshots changed while syncing.');
        changed.code = 'conflict'; throw changed;
      }
      if (!available.length) { fileId = ''; return null; }
      fileId = available[0].id;
      return Object.assign({},available[0],allMatches ? {copies:available.slice(1)} : {},
        appendOnly ? {parents:matches.map(snapshotKey)} : {});
    }

    async function upload(bytes, metadata) {
      var boundary = "physicskg-" + Math.random().toString(36).slice(2);
      var body = new Blob([
        "--" + boundary + "\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n",
        JSON.stringify(metadata),
        "\r\n--" + boundary + "\r\nContent-Type: " + metadata.mimeType + "\r\n\r\n",
        bytes,
        "\r\n--" + boundary + "--"
      ]);
      var response = await fetchImpl(
        DRIVE_UPLOAD_API + "?uploadType=multipart&fields=id,version,modifiedTime",
        {
          method: "POST",
          headers: headers({"Content-Type": "multipart/related; boundary=" + boundary}),
          body: body
        }
      );
      if (!response.ok) { throw apiError(response, "Could not create the Google Drive file"); }
      return {file:await response.json(),revision:response.headers.get('etag') || ''};
    }

    async function create(bytes) {
      if (allMatches && (await findMatches()).length) {
        var conflict = new Error('A tutorial cloud file was created by another device.'); conflict.code = 'conflict'; throw conflict;
      }
      var uploaded = await upload(bytes,{name:fileName,mimeType:mimeType}), result = uploaded.file;
      fileId = result.id;
      cache.delete(fileId);
      return {revision: uploaded.revision || String(result.version || "")};
    }

    async function append(bytes, parents) {
      if (parents.length > 30) {
        throw new Error('Too many concurrent tutorial snapshots in Google Drive.');
      }
      var properties = {};
      parents.forEach(function(parent,index) { properties['parent' + index] = parent; });
      await upload(bytes,{name:snapshotName,mimeType:mimeType,appProperties:properties});
    }

    async function update(bytes, revision) {
      var response = await fetchImpl(
        DRIVE_UPLOAD_API + "/" + encodeURIComponent(fileId) +
          "?uploadType=media&fields=id,version,modifiedTime",
        {
          method: "PATCH",
          headers: headers(Object.assign(
            {"Content-Type": mimeType},
            revision ? {"If-Match": revision} : {}
          )),
          body: bytes
        }
      );
      if (!response.ok) { throw apiError(response, "Could not update the Google Drive file"); }
      var result = await response.json();
      cache.delete(fileId);
      return {revision: response.headers.get("etag") || String(result.version || "")};
    }

    async function audioInventory() {
      var assets = new Map(), pageToken = '';
      do {
        var params = new URLSearchParams({
          q:"appProperties has { key='physicskgAsset' and value='tutorial-audio-v1' } and trashed = false",
          fields:'nextPageToken,files(id,mimeType,size,appProperties)',pageSize:'1000',spaces:'drive'
        });
        if (pageToken) { params.set('pageToken',pageToken); }
        var response = await fetchImpl(DRIVE_API + '?' + params,{headers:headers()});
        if (!response.ok) { throw apiError(response,'Could not list Google Drive tutorial recordings'); }
        var result = await response.json();
        for (var file of result.files || []) {
          var hash = file.appProperties && file.appProperties.sha256;
          if (!/^[a-f0-9]{64}$/.test(hash) || !Number(file.size) ||
              Number(file.size) > 50 * 1024 * 1024 || !/^audio\//.test(file.mimeType)) { continue; }
          if (!assets.has(hash)) { assets.set(hash,[]); }
          assets.get(hash).push(file);
        }
        pageToken = result.nextPageToken;
      } while (pageToken);
      return assets;
    }
    async function downloadAudio(file) {
      var response = await fetchImpl(DRIVE_API + '/' + encodeURIComponent(file.id) + '?alt=media',{headers:headers()});
      if (response.status === 404) { return null; }
      if (!response.ok) { throw apiError(response,'Could not download a Google Drive tutorial recording'); }
      return new Blob([await response.blob()],{type:file.mimeType});
    }
    async function uploadAudio(asset) {
      await upload(asset.blob,{
        name:'PhysicsKG audio ' + asset.id, mimeType:asset.mimeType,
        appProperties:{physicskgAsset:'tutorial-audio-v1',sha256:asset.id}
      });
    }

    return {
      read: read,
      appendOnly:appendOnly,
      audioInventory:audioInventory, downloadAudio:downloadAudio, uploadAudio:uploadAudio,
      write: function(bytes, syncOptions) {
        if (appendOnly) { return append(bytes, syncOptions && syncOptions.remote ? syncOptions.remote.parents : []); }
        return syncOptions && syncOptions.create
          ? create(bytes)
          : update(bytes, syncOptions && syncOptions.revision);
      },
      fileName: fileName
    };
  }

  global.kgCreateGoogleDriveAuthorizer = createAuthorizer;
  global.kgCreateGoogleDrivePersonalDataProvider = createProvider;
  global.kgGoogleDrivePersonalDataFileName = DEFAULT_FILE_NAME;
})(window);
