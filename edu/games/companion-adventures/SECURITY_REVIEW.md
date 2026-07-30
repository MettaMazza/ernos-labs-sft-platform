# Dependency security review

Review date: 30 July 2026
Scope: E01 companion adventure review 1.4.0
Remote hosting status: not authorised and not ready

The production build and six application/content tests pass with Node.js 22.
The application contains no server action, upload, sign-in, database, analytics
call or runtime application network request. Narration and effects are bundled
or produced locally.

The current dependency audit reports 15 inherited advisories: 2 low and 13
high. They are retained as an explicit hosting block. No force audit fix or
unreviewed major upgrade was applied to a visually verified child-facing build.

Before any public deployment, a future review must:

1. upgrade to stable patched dependencies;
2. repeat the production build, six automated tests and full device play test;
3. obtain a clean production audit or document a narrow reviewed exception;
4. confirm that offline audio, captions, local-only progress and network
   boundaries remain intact; and
5. receive Maria Smith's separate hosting authorisation.

The current source can be reviewed and versioned on GitHub `main`; it must not
be described as an approved or production-hosted child service.
