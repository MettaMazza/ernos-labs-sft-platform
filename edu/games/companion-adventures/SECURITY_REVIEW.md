# Dependency security review

Review date: 30 July 2026  
Scope: E01 companion adventure review 1.2.0  
Remote hosting status: not authorised and not ready

The production build and four application tests pass with Node.js 22. The app
contains no server action, user upload, sign-in, database, analytics call or
application network request. It is intended for local review only at this
stage.

`npm audit --omit=dev` still reports three high-severity advisories inherited
through the latest stable Next.js release available on the review date
(`16.2.12`): its bundled PostCSS and Sharp versions are inside the advisory
ranges. Forcing unrelated major dependency resolutions was rejected because it
would make the verified build less trustworthy.

This record does not dismiss those advisories. A future working version must:

1. upgrade to a stable upstream release containing patched transitive
   dependencies;
2. run the complete build and content tests;
3. obtain a clean production dependency audit, or record a reviewed and
   narrowly justified exception; and
4. remain unhosted until Maria Smith separately authorises deployment.

The current source may be reviewed and versioned on GitHub `main`; it must not
be represented as an approved or production-hosted child service.
