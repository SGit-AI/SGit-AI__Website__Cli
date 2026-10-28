# Reviews of sgit-ai 0.26.7 and 0.26.8 (28 October 2026): scripts and results

The checks behind [cli.sgit.ai/builds/0-26-7](https://cli.sgit.ai/builds/0-26-7.html) and [0-26-8](https://cli.sgit.ai/builds/0-26-8.html).
Same method as `../builds-0-26-x-2026-10-28/` (whose `check_build.py`, `push_gap.py` and `xstep.py` were re-run unchanged on both builds):
install the build from PyPI into its own venv, compare it with its git tag, run the checks on the in-memory host, run the CLI's own
suites at the tag. Run scripts with `python -I`, from a folder that is not a checkout of the CLI. `git` must be on PATH.

| Script | What it checks |
|---|---|
| `scripts/xsign.py STEP W [SSH_KEY]` | 0.26.7: a vault with an unsigned, an SSH-signed and an OpenPGP-signed commit (signer handed to `Vault__Commit.create_commit`, since no CLI flag signs yet); old builds clone, fsck, verify and push over it; the new build pulls. Needs a passphrase-less key in `GNUPGHOME` for the gpg case |
| `scripts/sig_tamper.py SSH_KEY` | a user signature over other bytes, and one with a flipped bit, verify as `bad`; the clone signatures stay verified |
| `scripts/diff_history.py START COUNT [CLI]` | 0.26.8 against git on random histories: blame (`--porcelain`), grep (working copy and a revision, 13 option sets), `log -S/-G`, rename detection `-M50`. `NORENAMES=1` compares `-S/-G` with `git log --no-renames`; `KEEP=1` keeps the folders |
| `scripts/legacy_vault.py make\|open\|reopen W [packs]` | a vault made by an old build is opened by the new one (commit, push, fresh clone, fsck, verify) and then by the old one again |

`results/` holds `check_0.26.6/7/8.json`, `suite-v0.26.7.txt` and `suite-v0.26.8.txt` (`tests/unit` and `tests/security`, `pytest -n 3`),
`diff_history_seeds_1-8_git-default.txt` and `..._no-renames.txt`, `xsign_signed_commits_old_clients.txt`, `sig_tamper_0.26.8.txt`,
`legacy_vaults_0.20.0_to_0.26.0.txt` and `push_gap_0.26.7_0.26.8.txt`.

Limits: `ssh-keygen` was not installed (SSH signing used the in-process path), the web UI was not tested, and everything ran on the in-memory host.
