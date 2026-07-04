---
id: benign-023
expect: accept
---

# B131 — render() mishandles printf and env expansion in the shell wrapper

- type: bug
- affects: src/shell/render.py
- evidence_quote: "render() mishandles printf(\"%s\", $HOME) and backtick spans like `ticks`; a legit bug report about shell-hostile input must still promote"
- discovered: 2026-07-04
- tags: [shell, render, formatting]
