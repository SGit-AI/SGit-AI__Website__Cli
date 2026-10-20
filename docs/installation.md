# Installation, cli.sgit.ai

> Install sgit with pip, verify with sgit doctor, upgrade with sgit update. Python 3.11+, two runtime dependencies.

*Source: <https://cli.sgit.ai/docs/installation.html> · generated from the same content as the page, so the two cannot drift. Moved from <https://sgit.ai/docs/installation.html> (sgit.ai v0.7.87) on 2026-10-20.*

---
# Installation

Pure Python, two runtime dependencies. Python 3.11 or newer.

```
$ pip install sgit-ai
# or, on externally-managed systems:
$ pipx install sgit-ai
```

This installs two entry points: `sgit` and `sgit-ai` (they are identical, use whichever you like).

## Verify

```
$ sgit version
sgit-ai v0.18.0
$ sgit doctor
✓ remote reachable   ✓ TLS ok   ✓ config valid
```

`sgit doctor` checks connectivity and configuration and prints per-OS fix instructions for the common problems (including SSL certificate issues). Add `--json` if a script or an agent is doing the checking.

## Upgrade

```
$ sgit update   # wraps pip install --upgrade sgit-ai
```

The current release is 0.21.0, published 10 October 2026. If `sgit version` still shows an older number after `sgit update`, you have more than one Python environment; run `python -m pip install --upgrade sgit-ai` in the one your tools use. What changed, what now refuses and what to do: [Update sgit-ai to 0.21.0](../docs/update-to-0-21-0.md). Coming from 0.17 or older, also read [Update sgit-ai to 0.18.0](../docs/update-to-0-18-0.md) for the clone command.

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/docs/installation.html)*
