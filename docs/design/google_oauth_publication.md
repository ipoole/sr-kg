# Google OAuth publication

This checklist records the public-facing configuration for making PhysicsKG's
optional Google Drive synchronisation available beyond named test users. It is
operational documentation, not a second source for runtime behaviour; the data
and security model remains in [Personal data](personal_data.md).

## Public assets

| Google field | Value |
| --- | --- |
| App name | `PhysicsKG` |
| App home page | `https://ipoole.github.io/sr-kg/` |
| Privacy policy | `https://ipoole.github.io/sr-kg/privacy.html` |
| Terms of service | `https://ipoole.github.io/sr-kg/terms.html` |
| App entry point | `https://ipoole.github.io/sr-kg/output/PhysicsKG.html` |
| Logo | `physicskg-logo-120.png` (120 by 120 pixels) |
| Authorised domain | `ipoole.github.io` |
| Authorised JavaScript origin | `https://ipoole.github.io` |
| OAuth scope | `https://www.googleapis.com/auth/drive.file` |
| Web client ID | `45956259452-4sd6v6vmi653bqfs5vfdcsn2bab85ea8.apps.googleusercontent.com` |

Choose the project's real user-support and developer-contact email addresses in
Google Cloud; they are account settings and are deliberately not stored here.

## Publish checklist

1. Merge and publish the home page, privacy policy and 120-pixel logo above, and
   check that each URL is public without signing in.
2. In Google Search Console, verify ownership of the authorised domain. Because
   PhysicsKG is a GitHub Pages project site, Google may require verification at
   the `ipoole.github.io` user-site root rather than only under `/sr-kg/`. If so,
   place Google's verification file or meta tag in the repository that publishes
   that root, or use a verified custom domain.
3. In Google Auth Platform **Branding**, enter the public URLs, upload the logo,
   choose the support email and submit any requested branding verification.
4. In **Audience**, keep the app external and choose **Publish app** when the
   branding fields and domain are accepted.
5. In **Data Access**, retain only `drive.file`; it permits access to files the
   app creates or that the user explicitly opens, rather than the user's whole
   Drive.
6. Confirm that the Google Drive API is enabled and the web client retains the
   authorised JavaScript origin above.
7. Test with a Google account that is not on the test-user list: connect, create
   or update `PhysicsKG personal data.zip`, sync in a second browser, disconnect,
   and revoke access from the Google Account permissions page.

If Google requests broader scope verification, first confirm that the scope has
not accidentally changed: the intended `drive.file` scope is non-sensitive and
is the narrowest permission that supports the visible archive design.
