# Graphite working prototype handoff

The approved prototype is implemented in prototypes/graphite. Local preview at
completion: http://127.0.0.1:64498/. It serves the isolated build worktree; its
prototype bytes match the integrated repository files. Reproduce from the
repository using the serve command in prototypes/graphite/README.md.

Lead: graphite-prototype-root. Builder: graphite_builder. Independent verifier:
prototype_verifier. Source commits integrated locally: 3f53607, ebb5751,
bed2360, 2ecc8c4, 796e50b. No remote push or production deployment performed.

## Verified

- Static check.py and node syntax check pass. Six local HTML pages, four source
  records, licensed local fonts/icons, no CDN dependency.
- Lead browser script: 8 scenario checks pass; screenshots 01–08.
- Independent matrix: desktop/mobile × dark/light plus no-JavaScript desktop
  and mobile, all source roundtrips, clipboard contents, keyboard and recovery.
- Lead axe-core 4.12.1 and independent axe-core 4.13.0 each report zero violations
  and zero incomplete home checks in four width/theme states.
- Initial layout/readability issues corrected; combined visual QA passes in
  prototypes/graphite/design-qa.md. Independent final delta review at796e50b.
- Current core board_init validated in disposable directory; retained scaffold
  and receipt under initialization-example/ and initialization-result.json.
- Existing connected Codex MCP tools also executed board_init and listed the
  resulting example project in a fresh disposable directory. Retained output
  is installed-mcp-initialization.json with scaffold under
  installed-initialization-example/. This verifies the actual tool handoff,
  without claiming a new plugin installation or new Codex session was tested.

## Boundaries

This is a prototype with synthetic, read-only data. It does not initialize a
repository from the browser, simulate installation success, change product-effect
criteria, publish a site, or resolve production B016/B017. No fresh Codex client
installation or real-user study was conducted. Local Chrome testing does not
establish universal browser or accessibility compliance. Manrope is a licensed
font substitute for the generated lettering, not a newly designed custom font.

Asset provenance: https://github.com/sharanda/manrope and
https://github.com/tabler/tabler-icons; pinned package sources and licenses are
under prototypes/graphite/assets. No paid font was installed.

Next step is owner inspection of the working prototype, followed by a separately
scoped rollout to the actual website/viewer/assets if approved. Lead owns retained
evidence in this directory. Agent cost and elapsed time: not measured.
