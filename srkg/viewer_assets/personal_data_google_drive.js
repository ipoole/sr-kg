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
      if (accessToken && global.google && global.google.accounts && global.google.accounts.oauth2) {
        global.google.accounts.oauth2.revoke(accessToken, function() {});
      }
      accessToken = "";
      expiresAt = 0;
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
    var fileId = "";

    function headers(extra) {
      var result = {Authorization: "Bearer " + token()};
      Object.keys(extra || {}).forEach(function(key) { result[key] = extra[key]; });
      return result;
    }

    async function findFile() {
      if (fileId) { return {id: fileId}; }
      var escapedName = fileName.replace(/'/g, "\\'");
      var params = new URLSearchParams({
        q: "name = '" + escapedName + "' and trashed = false",
        spaces: "drive",
        fields: "files(id,name,version,modifiedTime)",
        orderBy: "modifiedTime desc",
        pageSize: "10"
      });
      var response = await fetchImpl(DRIVE_API + "?" + params.toString(), {headers: headers()});
      if (!response.ok) { throw apiError(response, "Could not search Google Drive"); }
      var result = await response.json();
      var match = (result.files || []).find(function(item) { return item.name === fileName; });
      if (!match) { return null; }
      fileId = match.id;
      return match;
    }

    async function read() {
      var file = await findFile();
      if (!file) { return null; }
      var response = await fetchImpl(
        DRIVE_API + "/" + encodeURIComponent(file.id) + "?alt=media",
        {headers: headers()}
      );
      if (response.status === 404) { fileId = ""; return null; }
      if (!response.ok) { throw apiError(response, "Could not download personal data from Google Drive"); }
      return {
        bytes: await response.arrayBuffer(),
        revision: response.headers.get("etag") || ""
      };
    }

    async function create(bytes) {
      var boundary = "physicskg-" + Math.random().toString(36).slice(2);
      var body = new Blob([
        "--" + boundary + "\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n",
        JSON.stringify({name: fileName, mimeType: "application/zip"}),
        "\r\n--" + boundary + "\r\nContent-Type: application/zip\r\n\r\n",
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
      var result = await response.json();
      fileId = result.id;
      return {revision: response.headers.get("etag") || String(result.version || "")};
    }

    async function update(bytes, revision) {
      var response = await fetchImpl(
        DRIVE_UPLOAD_API + "/" + encodeURIComponent(fileId) +
          "?uploadType=media&fields=id,version,modifiedTime",
        {
          method: "PATCH",
          headers: headers(Object.assign(
            {"Content-Type": "application/zip"},
            revision ? {"If-Match": revision} : {}
          )),
          body: bytes
        }
      );
      if (!response.ok) { throw apiError(response, "Could not update the Google Drive file"); }
      var result = await response.json();
      return {revision: response.headers.get("etag") || String(result.version || "")};
    }

    return {
      read: read,
      write: function(bytes, syncOptions) {
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
