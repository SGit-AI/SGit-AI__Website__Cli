# sgit pki, cli.sgit.ai

> PKI key management and encryption

*Source: <https://cli.sgit.ai/reference/pki.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit pki

PKI key management and encryption.

*Generated from `sgit help all --format json`, sgit-ai v0.26.8. 10 subcommands below. To change this page, change the command's `register()` in the CLI and regenerate.*

```text
sgit pki
```

## Subcommands

- [`sgit pki contacts`](#pki-contacts): List imported contacts
- [`sgit pki decrypt`](#pki-decrypt): Decrypt a file with local key
- [`sgit pki delete`](#pki-delete): Delete key pair
- [`sgit pki encrypt`](#pki-encrypt): Encrypt a file for a recipient
- [`sgit pki export`](#pki-export): Export public key bundle (JSON)
- [`sgit pki import`](#pki-import): Import contact public key
- [`sgit pki keygen`](#pki-keygen): Generate encryption + signing key pair
- [`sgit pki list`](#pki-list): List local key pairs
- [`sgit pki sign`](#pki-sign): Sign a file (detached signature)
- [`sgit pki verify`](#pki-verify): Verify a detached signature

### sgit pki contacts {#pki-contacts}

List imported contacts

```text
sgit pki contacts
```

### sgit pki decrypt {#pki-decrypt}

Decrypt a file with local key

```text
sgit pki decrypt [options] <file>
```

| Argument | | What it is |
|---|---|---|
| `file` | required | Encrypted file (.enc) |

| Option | What it does |
|---|---|
| `--fingerprint` | Your encryption key fingerprint |
| `--output`, `-o` | Output file, or - for stdout (default: FILE without .enc) |

### sgit pki delete {#pki-delete}

Delete key pair

```text
sgit pki delete <fingerprint>
```

| Argument | | What it is |
|---|---|---|
| `fingerprint` | required | Encryption key fingerprint |

### sgit pki encrypt {#pki-encrypt}

Encrypt a file for a recipient

```text
sgit pki encrypt [options] <file>
```

| Argument | | What it is |
|---|---|---|
| `file` | required | File to encrypt |

| Option | What it does |
|---|---|
| `--fingerprint` | Your key fingerprint (for signing) |
| `--output`, `-o` | Output file (default: FILE.enc) |
| `--recipient` | Recipient fingerprint (a contact or one of your key pairs) |

### sgit pki export {#pki-export}

Export public key bundle (JSON)

```text
sgit pki export <fingerprint>
```

| Argument | | What it is |
|---|---|---|
| `fingerprint` | required | Encryption key fingerprint |

### sgit pki import {#pki-import}

Import contact public key

```text
sgit pki import <file>
```

| Argument | | What it is |
|---|---|---|
| `file` | required | Path to public key bundle JSON (or - for stdin) |

### sgit pki keygen {#pki-keygen}

Generate encryption + signing key pair

```text
sgit pki keygen [options]
```

| Option | What it does |
|---|---|
| `--label` | Label for the key pair |

### sgit pki list {#pki-list}

List local key pairs

```text
sgit pki list
```

### sgit pki sign {#pki-sign}

Sign a file (detached signature)

```text
sgit pki sign [options] <file>
```

| Argument | | What it is |
|---|---|---|
| `file` | required | File to sign |

| Option | What it does |
|---|---|
| `--fingerprint` | Signing key fingerprint |

### sgit pki verify {#pki-verify}

Verify a detached signature

```text
sgit pki verify [options] <file> <signature>
```

| Argument | | What it is |
|---|---|---|
| `file` | required | File to verify |
| `signature` | required | Signature file (.sig) |

| Option | What it does |
|---|---|
| `--json` | Print {valid, signing_fingerprint, signer_label, signer_source} as JSON |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/reference/pki.html)*
