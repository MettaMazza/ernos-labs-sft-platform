# Dependency security review

Review date: 31 July 2026
Scope: unified E01 through E04 companion adventure review 2.1.1
Remote hosting status: not authorised and not ready

The four-level application contains no server action, upload, sign-in, database,
analytics call or runtime application network request. Narration, music and
effects are bundled or produced locally. Level Four uses the same device-only
progress, hidden-page audio stop and offline media boundaries as Levels One
through Three.

The retained dependency audit reports 15 inherited advisories: 2 low and 13
high. They are retained as an explicit hosting block. No force audit fix or
unreviewed major upgrade was applied to a visually verified child-facing build.

Before any public deployment, a future review must:

1. upgrade to stable patched dependencies;
2. repeat the production build, automated tests and full device play test;
3. obtain a clean production audit or document a narrow reviewed exception;
4. confirm that offline audio, captions, local-only progress and network
   boundaries remain intact; and
5. receive Maria Smith's separate hosting authorisation.

The current source can be reviewed and versioned on GitHub `main`; it must not
be described as an approved or production-hosted child service.
