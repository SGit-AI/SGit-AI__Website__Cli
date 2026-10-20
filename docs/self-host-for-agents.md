# Self-hosting a vault server for agents, cli.sgit.ai

> Encrypted memory for agents in VMs, containers, a Mac mini or ephemeral jobs: run the SG/Send container with an access token and a storage folder, create the vault, the agent's clone-work-push entry point, Docker Compose, Kubernetes manifests, the cloud, a second server, what the server holds, and the errors you may meet (--endpoint, mcp<2, port 8080).

*Source: <https://cli.sgit.ai/docs/self-host-for-agents.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift. Moved from <https://sgit.ai/docs/self-host-for-agents.html> (sgit.ai v0.7.87) on 2026-10-20.*

---
# Self-hosting a vault server for agents

Encrypted memory for agents that run in isolated places: VMs, containers, a Mac mini, GPU machines, jobs that last one task. One SG/Send container with an access token, storage in a folder or an S3 bucket, and `sgit` in each agent. The server stores ciphertext; the agents and you hold the keys. The why, and five deployment patterns drawn as diagrams, are in the article [Encrypted memory for agents that run somewhere else](https://sgit.ai/articles/encrypted-memory-for-isolated-agents.html).

Tested on 8 October 2026 with sgit-ai 0.20.0 and sgraph-ai-app-send 0.33.0 (the package inside the image) against a local server. Sections that were not run here say so. Every server setting is documented in the [deployment docs](https://sgit.ai/deploy/index.html).

## 1. Run the server

With Docker, on any amd64 or arm64 machine, including Apple silicon:

```
$ export SG_ACCESS_TOKEN=$(openssl rand -hex 32)    # keep it in a password manager
$ docker run -d --name vault -p 127.0.0.1:8080:8080 \
    -e SGRAPH_SEND__ACCESS_TOKEN="$SG_ACCESS_TOKEN" \
    -v "$PWD/sg-data:/data" diniscruz/sg-send-vault:v0.33.0
```

Without Docker, from pip, which runs the same code with the same command as the image:

```
$ pip install sgraph-ai-app-send "mcp<2"
$ SEND__STORAGE_MODE=disk SEND__DISK_PATH=./sg-data \
  SGRAPH_SEND__ACCESS_TOKEN="$SG_ACCESS_TOKEN" \
  python -m sgraph_ai_app_send__docker.serve
```

Check it, with and without the token:

```
$ curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8080/api/info/health
401
$ curl -H "x-sgraph-access-token: $SG_ACCESS_TOKEN" http://localhost:8080/api/info/health
{"status":"ok"}
```

| Setting | Values | Notes |
|---|---|---|
| `SGRAPH_SEND__ACCESS_TOKEN` | a long random string | Gates every route, reads included. Header `x-sgraph-access-token`; the browser UI has a sign-in form. |
| `SEND__STORAGE_MODE` | `disk`, `s3`, `memory` | The image sets `disk`. `memory` is emptied by a restart. |
| `SEND__DISK_PATH` | a path | The image uses `/data`. This folder is the whole memory: back it up. |
| `SEND__S3_BUCKET` | a bucket name | For `s3` mode, with the usual AWS credentials. Needed for more than one replica. |

## 2. Create the memory vault

From the machine you administer from, not from an agent:

```
$ mkdir memory && cd memory && mkdir -p agents/a1 agents/a2 shared
$ echo "# a1 notes" > agents/a1/notes.md; echo "# a2 notes" > agents/a2/notes.md; echo "# brief" > shared/brief.md
$ sgit init --base-url http://localhost:8080 --token "$SG_ACCESS_TOKEN" .
Vault created!  Vault ID: …
  Vault key: …            # the whole credential: store it now, show it to no one
$ sgit commit "memory layout"
$ sgit push --token "$SG_ACCESS_TOKEN"
Pushed 1 commit(s), 3 object(s) uploaded.
```

Use `--base-url`. The deployment docs show `--endpoint` in three places; sgit 0.20.0 answers `unrecognized arguments: --endpoint`.

## 3. The agent's entry point

The whole memory protocol, run once per task. It expects the base URL, the access token, the agent's id, and a file holding the key to its vault:

```
#!/bin/sh
set -e
sgit clone --base-url "$SG_BASE_URL" --token "$SG_ACCESS_TOKEN" \
     --path "agents/$AGENT_ID" --depth 1 "$(cat "$VAULT_KEY_FILE")" /work/memory
cd /work/memory
# ... the agent reads agents/$AGENT_ID/, does one task, writes what it learned ...
sgit commit "$AGENT_ID run $(date -u +%FT%TZ)"
sgit push                     # pulls first; uses the token the clone saved
```

Run as written against the local server: the clone held one folder, the commit and push uploaded one object, and a full clone elsewhere pulled the change.

- **`--path` and `--depth 1`** keep the start fast as the vault grows: one folder of a 600-commit vault in 14 s, against 80 s for all of it ([Partial clones](../docs/partial-clones.md)).
- **`--path` is not an access boundary.** The clone holds the vault key, and `sgit fetch agents/a2` widens it to another agent's folder. For agents that must not read each other's memory, use one vault per agent, and read keys for what an agent only reads.
- **The clone keeps the vault key and the access token** in `.sg_vault/local/`, so that `sgit push` works without them on the command line. Delete the working directory, or the container, when the task ends.
- Several agents pushing to one vault is the setup in [Agents sharing one vault](../docs/agents-sharing-one-vault.md).

## 4. Docker Compose: a Mac mini or any single host

```
services:
  vault:
    image: diniscruz/sg-send-vault:v0.33.0
    environment:
      SEND__STORAGE_MODE: disk
      SEND__DISK_PATH: /data
      SGRAPH_SEND__ACCESS_TOKEN: ${SG_ACCESS_TOKEN}
    volumes:
- ./sg-data:/data
    ports:
- "127.0.0.1:8080:8080"
    restart: unless-stopped

  agent-a1:
    image: your-agent-image          # anything with sgit-ai and the entry point above
    environment:
      SG_BASE_URL: http://vault:8080
      SG_ACCESS_TOKEN: ${SG_ACCESS_TOKEN}
      AGENT_ID: a1
      VAULT_KEY_FILE: /run/secrets/a1_vault_key
    secrets: [a1_vault_key]
    depends_on: [vault]

secrets:
  a1_vault_key:
    file: ./keys/a1.vault-key
```

Not run here: this session had no Docker daemon. It uses only the image's documented settings.

Back up `./sg-data` with whatever you already use for folders. It holds ciphertext, hashes and vault ids, so the backup does not need to be trusted with the contents. To reach the server from other devices, put TLS in front (the deployment docs suggest Caddy) on a network you control; the vault UI needs a secure context in the browser.

## 5. Kubernetes

One Deployment for the server, a Service only the cluster can reach, a NetworkPolicy that admits only agent pods, and a Job per agent task. Create the secrets first:

```
$ kubectl create namespace agent-memory
$ kubectl -n agent-memory create secret generic vault-access-token --from-literal=token="$SG_ACCESS_TOKEN"
$ kubectl -n agent-memory create secret generic agent-a1-vault-key --from-file=vault-key=./keys/a1.vault-key
```

```
apiVersion: v1
kind: PersistentVolumeClaim
metadata: {name: vault-data, namespace: agent-memory}
spec:
  accessModes: [ReadWriteOnce]
  resources: {requests: {storage: 10Gi}}
---
apiVersion: apps/v1
kind: Deployment
metadata: {name: sg-send-vault, namespace: agent-memory}
spec:
  replicas: 1                       # disk storage: one writer. More replicas need SEND__STORAGE_MODE=s3
  strategy: {type: Recreate}
  selector: {matchLabels: {app: sg-send-vault}}
  template:
    metadata: {labels: {app: sg-send-vault}}
    spec:
      containers:
- name: vault
          image: diniscruz/sg-send-vault:v0.33.0
          ports: [{containerPort: 8080}]
          env:
- {name: SEND__STORAGE_MODE, value: disk}
- {name: SEND__DISK_PATH, value: /data}
- name: SGRAPH_SEND__ACCESS_TOKEN
              valueFrom: {secretKeyRef: {name: vault-access-token, key: token}}
          volumeMounts: [{name: data, mountPath: /data}]
      volumes:
- {name: data, persistentVolumeClaim: {claimName: vault-data}}
---
apiVersion: v1
kind: Service
metadata: {name: vault, namespace: agent-memory}
spec:
  type: ClusterIP
  selector: {app: sg-send-vault}
  ports: [{port: 8080, targetPort: 8080}]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: vault-from-agents-only, namespace: agent-memory}
spec:
  podSelector: {matchLabels: {app: sg-send-vault}}
  policyTypes: [Ingress]
  ingress:
- from: [{podSelector: {matchLabels: {role: agent}}}]
      ports: [{port: 8080}]
---
apiVersion: batch/v1
kind: Job
metadata: {generateName: agent-a1-, namespace: agent-memory}   # kubectl create, not apply
spec:
  backoffLimit: 0
  ttlSecondsAfterFinished: 600
  template:
    metadata: {labels: {role: agent}}
    spec:
      restartPolicy: Never
      containers:
- name: agent
          image: your-agent-image
          command: ["/entrypoint.sh"]
          env:
- {name: SG_BASE_URL, value: "http://vault:8080"}
- {name: AGENT_ID, value: a1}
- {name: VAULT_KEY_FILE, value: /secrets/vault-key}
- name: SG_ACCESS_TOKEN
              valueFrom: {secretKeyRef: {name: vault-access-token, key: token}}
          volumeMounts:
- {name: key, mountPath: /secrets, readOnly: true}
- {name: work, mountPath: /work}
      volumes:
- {name: key, secret: {secretName: agent-a1-vault-key}}
- {name: work, emptyDir: {}}
```

Not run on a cluster for this guide; it parses as YAML and uses only the image's documented settings. A NetworkPolicy only takes effect with a network plugin that enforces it.

## 6. The cloud

The deployment docs have CloudFormation templates for [Lambda, Fargate and EC2](https://sgit.ai/deploy/index.html), marked as written and lint-clean with live validation in progress. As written they put a public endpoint in front: a Function URL, a load balancer, or an instance with its own certificate. For agents, the shape the article draws keeps everything the agents talk to inside the VPC: an internal load balancer with a private address, and behind it either the container (EC2, Fargate or Kubernetes) or the same app on Lambda attached to the VPC, both with `s3` storage through a VPC endpoint; a VPN to any machine outside; and CloudFront with a VPC origin if you want the vault UI from a phone. Treat that as a design to adapt the templates to, not a template.

## 7. A second server

```
$ sgit remote add origin https://vault.home.example --default
$ sgit remote add backup https://vault.cloud.example
$ sgit push --remote backup
Vault structure re-synced to server.
```

The second server then holds the same encrypted vault, and a clone from it matches. Servers do not replicate to each other: schedule the push to `backup`, or have agents push to both. A server that lost the vault, a `memory`-mode server after a restart for example, is restored by the same push from any clone with the vault key; tested here, the fresh clone came back at the same commit.

## 8. What the server holds

After the tests on this page the test vault's storage was 26 files, 228 KB: encrypted objects named by hash, encrypted keys, refs, and a manifest of three fields, the vault id, a hash of the write key and the creation time. A search of all of it for the text the agents wrote, and for the file and folder names, found nothing. Someone with the storage can see vault ids, sizes and timing, and can delete; they cannot read. The keys are with the agents and with you, so protect those places: ephemeral containers, secrets mounted only where needed, one vault per trust boundary.

## When something goes wrong

| You see | What it means | Do this |
|---|---|---|
| `unrecognized arguments: --endpoint` | The flag in the deployment docs is not the CLI's | Use `--base-url` |
| `401` from the server | No token, or the wrong one | Pass `--token`, or the `x-sgraph-access-token` header |
| `Server.__init__() takes 2 positional arguments but 3 were given` at start-up | A pip install pulled `mcp` 2.x | `pip install "mcp<2"` |
| `address already in use` on 8080 | The serve module binds 8080 | Map another host port in Docker, or run `uvicorn sgraph_ai_app_send__docker.app:create_app --factory --port 8081` |
| `warning: you are using a PRIVATE key against a plain http:// URL` | The token travels in the clear, and the key is in argv | Fine on one host's Docker network; put TLS in front beyond it |
| A clone fails after the server restarted | `memory` mode was emptied | `sgit push` from any clone, or use `disk` or `s3` |
| `sgit doctor` reports the token rejected while push works | Seen in this test: doctor did not use the token saved by `--token` | Trust a real `sgit push` or the health check with the header |

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/docs/self-host-for-agents.html)*
