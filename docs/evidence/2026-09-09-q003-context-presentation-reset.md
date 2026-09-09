# Q003 context-presentation reset diagnostic — 2026-09-09

## Decision and boundary

The repository owner confirmed that the original Q003 `$WSL_SCRATCH`
artifacts are permanently lost and authorized a clean protocol reset. The
three earlier campaigns remain invalid and excluded. No prior response,
receipt, prompt, review, or generator was reused.

The reset ran a complete four-arm factorial for proposal case `D1-V4-C04`:

- raw Engineering Board JSON before case evidence;
- shipped prompt-guard prose before case evidence;
- raw Engineering Board JSON after case evidence; and
- shipped prompt-guard prose after case evidence.

This is one non-scored case under one current client. It can select or falsify
a presentation mechanism for later validation. It cannot establish product
effect, lock the proposal corpus, or change an H### epistemic status.

## Frozen inputs

- Campaign: `q003-presentation-reset-20260909-v1`
- Source commit: `9fa969a5658775d8e53c90a55996fa1507529c50`
- Source-tree SHA-256: `f473838759b3f0cc0136b6cb917a69bc65c49c9c81ad81c50e487aaf8acfe639`
- Bound source records: 32, including all 26 proposal evidence and fixture files
- Proposal corpus SHA-256: `ccdebc8be431047341bb13920d04fdc9a901e34664da6c90ed53f38be14ef662`
- Fixture SHA-256: `21224482fb9c7881ccf1314e9b33a52b76847b148324d89ee026668ae0c14e8a`
- Frozen core SHA-256: `80f28ae659518d9d4fd3d2132c32f824bc7827a8ba69c72115a3b013e06bcbcb`
- C04 context fingerprint: `ctx-3f38c2dc281d449f`
- Common-input SHA-256: `4c525305c62c7f049e0e01adaa9a367f18d60b0e4d0b67a41328ef706042e1f9`
- Client: Codex CLI 0.153.4
- Model: `gpt-5.6-sol`
- Reasoning effort: `medium`
- Sandbox: read-only
- Approval policy: never
- Sessions: ephemeral and isolated
- Tool calls: forbidden

The exact historical harness reproduced the macOS `/var` alias defect from
the named commit. It ran unchanged with `TMPDIR=/private/tmp`, the canonical
target of that root-owned alias. This environment value is recorded in the
audit and does not change any trial input.

## Preflight and execution integrity

The independent preflight passed 92 checks before freeze. It independently
derived the treatment mapping, execution order, and blind-review order. It
verified the exact Git commit and clean checkout, every committed source byte,
the complete 26-file proposal tree, prompt-only arm directories, client and
model pins, prompt hashes, schema, frozen core, fixture, corpus, and the empty
prior-artifact reuse list.

- Manifest SHA-256: `154591a5851ad9b44cf9b08de6fabf533cc8d336f8cf1d72ff24657b8068c0e9`
- Sealed mapping SHA-256: `ab1fe3609f63cb080fa7439f94a102989cb015ebac55d94d0dc7411b99f5b45e`
- Audit SHA-256: `c07b67e60d0a1d3fc5bb00b3101318ef249d8c53a825e17d710d825461990854`
- Freeze SHA-256: `053f0134237298ea93464164112cd4024d6b9139202f28aa5cfc597ca6c7e508`
- Post-freeze corrections: zero
- Retries or replacements: zero

Each arm has one exclusive start record and one appended end record. Every
process exited 0 with empty stderr. The four JSONL streams contain one unique
thread, one turn, and one `agent_message` each; no tool call appears. Each
response equals its stream message and has the exact response-schema fields.

| Treatment | Prompt SHA-256 | Receipt SHA-256 | Response SHA-256 |
|---|---|---|---|
| prose after | `041a64a4199d5a2a0005e2ae521e81c94cb1b9f3f4b13d9df472bc94eff53ffe` | `8b981fdf2bb7b067b7a5aadb1dacdf4f121459b6ff0ae85c8d05db8c0f757385` | `903b758de6ea5a8d590d963f03dc93fc81baec425bb30f1753aa350875173007` |
| prose before | `6576b8a91bec42a1f6ca4ead37cc4010700d85d32075e5901a39c6ab8881dc49` | `038a4b7ee37ae1ef73586350d3d9e175a61f910a78f0d81208d3aeb31e2c6752` | `504c9671f34c23b8cddcd85a87ab24bab411345625c95fde02a8df91e357a857` |
| raw after | `b7589fc695fd7932122887a9a83fdbf7908a9f0935dd8c88114bb6a2df95b212` | `283932d34a11792036ac88772f9b1404b0ac06e9239282b593f3d1dceb1ee4b3` | `2d0cd2691c59bbb24435bbf14eb34b39b2f406db1cd6e1a1cbac4bc91d82fc4e` |
| raw before | `abb55ffa09f0966e1dc7c4db7c28535b02c9c5eeeb4a35066e408fcfa6efb06a` | `cadb887532d9097c055bd8d632e5b40fa320f87fe9cc0ba7f3b3f87da908dd6f` | `049ae6d64c48f970db51b279e02088887e88407c2fa47eddad3155753ce1d907` |

## Blind review

The reviewer received four response-only objects in an independently derived
order. Its prompt contained no arm name, treatment label, mapping, or trial
prompt. The mapping was revealed only after the schema-valid blind review
completed.

- Review-packet SHA-256: `149f9f514a17e6d6b0b7a092c08503c724a53329f09f8f3b34b27506bb96e16f`
- Review-prompt SHA-256: `2b7f9561ce266a544230b86c02be5dc7c2489a7bb3b957ac4c7866e33178f7a2`
- Sealed review-map SHA-256: `78f480fba98612c6960de7f1934f6b0ee96f805dc146fdb76a266918a9eb7200`
- Blind-review SHA-256: `4ac0513f26c397dcd64e48b4f4c4c21c63aef31beda539918655099b301038f3`
- Blind-review receipt SHA-256: `98e2ec71352bf983f60bcbce2846caf5b6cf1949e6dec86f84799e7cdb76f2a8`
- Final result SHA-256: `39ea6f1178b74db3170da99be10697258cc8aaa4d7a9ac6847ab70d7e250e27d`

| Treatment | First-cause scope | Prior CLI incident | Memory use | Epistemic disposition |
|---|---|---|---|---|
| prose after | current incident only | not mentioned | mentioned, not used | proposed preserved |
| prose before | current incident only | not mentioned | mentioned, not used | proposed preserved |
| raw after | current incident only | not mentioned | mentioned, not used | proposed preserved |
| raw before | current incident only | not mentioned | mentioned, not used | proposed preserved |

Post-reveal inspection agreed with the blind classifications:

- Prose after first identified a missed or coalesced extension cache invalidation.
- Prose before first identified stale extension status after the branch round-trip.
- Raw after first identified missed or misordered extension-local transition invalidation.
- Raw before first identified extension cache invalidation failure.

Every response proposed a local extension correction, cited only
`E-D1-V4-C04`, set `durable_systemic_conclusion` to false, and explicitly left
H104 unproven. None connected the editor-extension symptom to the prior
command-line index incident in its first stated cause.

## Finding

Raw versus shipped prose and before versus after evidence produced zero of four
strict cross-incident first causes. Presentation format and position are not
sufficient for C04 under this current-client, single-case diagnostic.

This result falsifies presentation-only changes as the next mechanism for C04.
It does not prove that presentation never matters, estimate an effect size,
establish a general model limitation, authorize a scored baseline, lock
version 4, or establish product effect. The next product decision must concern
the memory-use contract or an explicitly different information boundary, not
another rearrangement of the same context.

## Durable evidence boundary

The raw campaign remains in a bounded external workspace. This document keeps
the source identity, complete response-relevant observations, arm and review
hashes, receipt hashes, and bounded conclusion in Git. Losing the external
workspace cannot turn the result into stronger evidence, but it also cannot
erase the recorded first-cause classifications or their source links.
